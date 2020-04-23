from flask import Flask, render_template, url_for, request, jsonify

app = Flask(__name__)

from geoportal import views