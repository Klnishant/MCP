from dotenv import load_dotenv, find_dotenv
import os
import pandas as pd
import matplotlib.pyplot as plt
import json
from flask import Flask, request, jsonify
import unicodedata
import base64
from datetime import datetime
from fpdf import FPDF

load_dotenv(find_dotenv())

app = Flask(__name__)

Google_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
Search_Engine_ID = os.environ.get("SEARCH_ENGINE_ID", "")

