/*
 * Main Javascript file for esso_admin.
 *
 * This file bundles all of your javascript together using webpack.
 */

// JavaScript modules
require('jquery');
require('font-awesome-webpack');
require('popper.js');
require('bootstrap');
import dt from 'datatables.net';

// Your own code
require('./plugins.js');
require('./script.js');
