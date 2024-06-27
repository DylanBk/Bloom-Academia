from flask import Flask, render_template, url_for, request, redirect, session
from . import db_functions as db
import bcrypt
import base64
import random