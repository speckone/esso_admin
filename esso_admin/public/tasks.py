import os
from flask import current_app
from celery.signals import celeryd_after_setup
from celery.utils.log import get_task_logger
import serial
import time
import math
from esso_admin.extensions import celery
from celery import group

logger = get_task_logger(__name__)

COMPORT = "COM8"
COMPORT = "/dev/ttyUSB0"
BAUD = 57600
polargraph_ready_seen = False
serial_port = None

polargraph_width_in_mm = 644  # Width between pulleys
polargraph_height_in_mm = 610  # Height of machine
polargraph_home_x_in_mm = polargraph_width_in_mm / 2  # Home postition X
polargraph_home_y_in_mm = 322  # Home position Y
polargraph_pulley_circumference_in_mm = 130  # Effective circumference of pulleys
polargraph_steps_per_rev = 400  # Number of whole steps per revolution for motors
polargraph_steps_multiplier = 1  # Stepper driver multiplier
polargraph_motor_max_speed = 600  # Max motor speed
polargraph_motor_acceleration = 400  # How quickly the motor accelerates to get to its top speed
polargraph_pen_up_setting = 180  # Servo 'up' position
polargraph_pen_down_setting = 107  # Servo 'down' position

page_width_in_mm = 610  # Drawing area in mm
page_height_in_mm = 489  # Drawing area in mm
page_x_offset_in_mm = 17  # How far (in mm) from the edge of the left pullley is the paper?
page_y_offset_in_mm = 120  # How far (in mm) down from the imaginary line drawn between motor spindles?


@celeryd_after_setup.connect
def connect_serial(sender, instance, **kwargs):
    global serial_port
    serial_port = serial.Serial(COMPORT, BAUD, timeout=10)
    logger.warn("Connected: %s" % serial_port.isOpen())


def get_string_lengths(x, y):
    whole_steps_per_mm = float(polargraph_steps_per_rev) / float(polargraph_pulley_circumference_in_mm)
    c = polargraph_width_in_mm - x
    len1 = math.sqrt((x * x) + (y * y))
    len2 = math.sqrt((c * c) + (y * y))
    steps1 = len1 * whole_steps_per_mm
    steps2 = len2 * whole_steps_per_mm

    # round the values to the nearest integer for output
    steps1_rounded = int(round(steps1))
    steps2_rounded = int(round(steps2))
    return steps1_rounded, steps2_rounded


@celery.task(ignore_result=True)
def write_command(command):
    # Attempt to simplify the serial read/write logic
    # Write one command only and return ready to calling function (let calling function deal with iterables)

    global polargraph_ready_seen

    logger.warn("")
    logger.warn("=================================")
    logger.warn("Call to writeCommandToPolargraph")
    logger.warn("")

    exit_flag = False

    while True:
        # logger.warn("")
        # logger.warn("Debug: Reading serial port section starts here:")

        number_of_bytes_waiting = serial_port.in_waiting
        if number_of_bytes_waiting > 0:
            logger.warn("Debug: Bytes waiting in serial port = %s" % number_of_bytes_waiting)

        data_read = serial_port.read(number_of_bytes_waiting).strip().decode()
        time.sleep(0.1)

        if "READY" in data_read or polargraph_ready_seen == True:
            # logger.warn("Debug: In 'READY' case: data_read should be 'READY' (is '%s')
            # or polargraphReadySeen should be true (is '%s')" % (data_read, polargraphReadySeen))
            if not exit_flag:
                # logger.warn("Debug: exitFlag should be false here. Is %s" % exitFlag)
                logger.warn("Write command: %s" % command)
                # serialPort.flush()
                serial_port.write(command.encode('ascii'))

                polargraph_ready_seen = False
                exit_flag = True

            else:
                # logger.warn("Debug: exitFlag should be true here. Is '%s'.
                # Setting polargraphReadySeen flag to true" % exitFlag)
                logger.warn("MSG: '%s'" % data_read)
                logger.warn("")
                logger.warn("Exiting writeCommandToPolargraph2")
                logger.warn("=================================")
                logger.warn("")

                polargraph_ready_seen = True
                return "DONE"

        elif not data_read:
            # logger.warn("Debug: data_read is '%s', ignoring..." % data_read)
            pass
        # If data_read doesn't contain 'READY' or is not 'NULL' then it is probably an error message or other info
        else:
            # logger.warn("Debug: data categorised as 'Not null' or not 'READY'. logger.warn data and move on. data_read is '%s'" % data_read)
            logger.warn("MSG: '%s'" % data_read)


@celery.task(ignore_result=True)
def load_setup():
    # Calculate where the home position is in steps
    # (Tested this and it revealed an error in my previously asserted home position. Updated measurements)
    polargraph_home_x_in_steps, polargraph_home_y_in_steps = get_string_lengths(polargraph_home_x_in_mm,
                                                                                polargraph_home_y_in_mm)
    logger.warn("Debug: Calculated home position = %s, %s" % (polargraph_home_x_in_steps, polargraph_home_x_in_steps))

    # Build the commands to setup the machine. Pulls settings from config variables at top of this script
    setup_commands = ["C02,0.36,END\n",
                      "C24," + str(polargraph_width_in_mm) + "," + str(polargraph_height_in_mm) + ",END\n",
                      "C29," + str(polargraph_pulley_circumference_in_mm) + ",END\n",
                      "C30," + str(polargraph_steps_per_rev) + ",END\n",
                      "C31," + str(polargraph_motor_max_speed) + ",1,END\n",
                      "C32," + str(polargraph_motor_acceleration) + ",1,END\n",
                      "C37," + str(polargraph_steps_multiplier) + ",END\n",
                      "C45," + str(polargraph_pen_up_setting) + "," + str(
                          polargraph_pen_down_setting) + ",1,END\n",
                      "C09," + str(polargraph_home_x_in_steps) + "," + str(
                          polargraph_home_y_in_steps) + ",END\n", "C13," + str(polargraph_pen_up_setting) + ",END\n",
                      "C14," + str(polargraph_pen_down_setting) + ",END\n"]

    logger.warn("Debug: Command list contains %s" % (setup_commands,))
    logger.warn("")
    logger.warn("Setting up the controller...")
    logger.warn("")

    # job = group(write_command.s(command) for command in setup_commands)
    # job.apply_async()
    for command in setup_commands:
        write_command(command)

    logger.warn("")
    logger.warn("Setup done!")


@celery.task(ignore_result=True)
def load_file(pg_file_name):
    filename = os.path.join(current_app.config['APP_DIR'], 'static', pg_file_name)
    with open(filename) as pg_file:
        job = group(write_command.s(line) for i, line in enumerate(pg_file))
        job.apply_async()
