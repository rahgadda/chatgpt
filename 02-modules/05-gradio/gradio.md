# Gradio

## Overview
- Gradio is an open-source Python library that is used to build machine learning and data science demos and web applications.
- `Interface` class can wrap any Python function with a user interface. It accepts below parameters
  - **fn:** Python function to wrap a UI around
  - **inputs:** Input component(s) (e.g. "text", "image" or "audio")
  - **outputs:** Output component(s) (e.g. "text", "image" or "label")

## Installation
- Gradio requires Python 3.7 or higher.
- Steps to execute hello world
  ```bash
  cd 02-modules/05-gradio
  pip  install -r requirements.txt
  python hello.py
  ```
- System will create [URL]( http://localhost:7860/), [Dark Theme URL]( http://localhost:7860/?__theme=dark)