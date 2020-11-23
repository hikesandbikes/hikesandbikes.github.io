---
layout: post
title: "Problem Set 7: Web Programming"
date: 2020-11-14
---

<h1>Answers to CS50x 2019 {{page.title}}.
</h1>

<h3>Similarities </h3>
<PRE>
helpers.py solution

def sentences(a, b):
    """Return sentences in both a and b"""
    a_sentences = set(sent_tokenize(a))
    b_sentences = set(sent_tokenize(b))

    return a_sentences & b_sentences


def substring_tokenize(str, n):
    substrings = []

    for i in range(len(str) - n + 1):
        substrings.append(str[i:i + n])


    return substrings


def substrings(a, b, n):
    """Return substrings of length n in both a and b"""

    a_substrings = set(substring_tokenize(a, n))
    b_substrings = set(substring_tokenize(b, n))

    return a_substrings & b_substrings

</PRE>

<h3>Survey </h3>
<PRE>
application.py solution

import cs50
import csv

from flask import Flask, jsonify, redirect, render_template, request

    # Configure application
    app = Flask(__name__)

    # Reload templates when they are changed
    app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def after_request(response):
    """Disable caching"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET"])
def get_index():
    return redirect("/form")


@app.route("/form", methods=["GET"])
def get_form():
    return render_template("form.html")


@app.route("/form", methods=["POST"])
def post_form():
    if not request.form.get("name"):
        return render_template("error.html", message="You did not provide a name.")
    file = open("survey.csv", "a")
    writer = csv.writer(file)
    writer.writerow((request.form.get("name"), request.form.get("position"), request.form.get("house")))
    file.close()
    return redirect("/sheet")

@app.route("/sheet", methods=["GET"])
def get_sheet():
    file = open("survey.csv", "r")
    reader = csv.reader(file)
    students = list(reader)
    return render_template("registered.html", students=students)


</PRE>
