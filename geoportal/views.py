from flask import render_template, url_for, request, jsonify, redirect, flash
from geoportal import app


@app.route('/')
def main():
    return render_template('home.html')
