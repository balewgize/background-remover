<a name="readme-top"></a>

<div align="center">
  <h3 align="center">Background remover</h3>

  <p align="center">
    Remove background from images using pre-trained ML models.
    <br />
    <a href="https://bgremover.streamlit.app/" target="_blank"><strong>View Demo »</strong></a>
    <br />
  </p>
</div>

<!-- ABOUT THE PROJECT -->
## About The Project

[![Screenshot](screenshot/example.png?raw=true "Tomar")](https://bgremover.streamlit.app/)

A web app built with ```Python``` and ```Streamlit``` that enables users to remove background from images using pre-trained ML models.

It does well for most images that doesn't have messy background but I'm sure you won't expect photoshop like results :) 

### Features
- Downloadable final result
- Transparent background
- Support multiple images

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With
- Python
- <a href="https://github.com/danielgatis/rembg" target="_blank">Rembg</a>
- <a href="https://streamlit.io/" target="_blank">Streamlit</a> 

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

* Python

### Installation

1. Clone the repo and navigate to ```background-remover``` directory 
   ```
   git clone https://github.com/balewgize/background-remover.git
   ```
   ```
   cd background-remover
   ```
2. Install required packages (virtual environments recommended)
   ```
   python3 -m venv venv && source venv/bin/activate
   ```
   ```
   pip install -r requirements.txt
   ```
3. Run the app using streamlit
   ```
   streamlit run bg_remover.py
   ```
4. Goto http://localhost:8501 on your browser

<p align="right">(<a href="#readme-top">back to top</a>)</p>

Thanks!
