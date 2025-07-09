<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links



<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support">
    <img src="Icon/IMAGE_Pothole_Int_small.png" alt="Logo" width="80" height="100">
  </a>

<h3 align="center">Pothole Detection for shock absorption support</h3>

  <p align="center">
    A machine vision project
    <br />
    <a href="https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support">View Demo</a>
    &middot;
    <a href="https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/issues/new">Report Bug</a>
    &middot;
    <a href="https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/pulls">Pull Request</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#usage">Usage</a></li>
      <ul>
        <li><a href="#training">Training</a></li>
        <li><a href="#running-inference">Running Inference</a></li>
        <li><a href="#camera-frustum">Camera frustum</a></li>
      </ul>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

This repository implements a monocular-vision pothole detection system that not only identifies pothole regions in a video stream, but also estimates each pothole’s real-world size and distance from the camera—all without relying on an expensive depth sensor. By combining state-of-the-art object detection with classical computer-vision techniques and camera calibration, the system delivers actionable data for smart suspension and road-maintenance applications.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [![Next][Python]][Python-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

1. Clone the repo
   ```sh
   git clone https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support.git
   ```
2. Install python packages
   ```sh
   pip install ultralytics opencv-python numpy pyqt6
   ```
3. Download the model files via git lfs
   ```js
   git lfs install
   git lfs pull
   ```
   if you haven't install git lfs, refer to the following doc: https://docs.github.com/en/repositories/working-with-files/managing-large-files/installing-git-large-file-storage

4. Change git remote url to avoid accidental pushes to base project
   ```sh
   git remote set-url origin AlterraFa/Pothole-Detection-for-shock-absorption-support
   git remote -v # confirm the changes
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

### Training
  To train YOLO model with a different dataset or with another model configuration
  1. Enter directory `Train`
     ```sh
     cd Train/
     ```
  2. Edit the `PotholeV8.py` file 
  3. Initialize and run training program
     ```sh
     ./scheduler.sh <directory_path> <batch_size> <epochs> -m <model_name> [-f <freeze_layers>]
     ```
### Running Inference
  - To run a simple debugging, simply run: 
     ```sh
     python3 Testbench.py
     ```
  - or using our custom UI:
     ```sh
     python3 UI.py
     ```
### Camera frustum
  - Visualizing our monocular camera model for depth estimation
     ```
     python3 3DCameraModel.py
     ```
_For further read, please refer to the [Documentation](./Document.pdf)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- ROADMAP -->
<!-- ## Roadmap

- [ ] Feature 1
- [ ] Feature 2
- [ ] Feature 3
    - [ ] Nested Feature

See the [open issues](https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p> -->



<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!


<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Top contributors:

<a href="https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AlterraFa/Pothole-Detection-for-shock-absorption-support" alt="contrib.rocks image" />
</a>



<!-- LICENSE -->
## License

Distributed under the project_license. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Nguyen Trinh Tra Giang - ntony8124@gmail.com

Project Link: [https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support](https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support)

<p align="right">(<a href="#readme-top">back to top</a>)</p>




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/AlterraFa/Pothole-Detection-for-shock-absorption-support.svg?style=for-the-badge
[contributors-url]: https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/AlterraFa/Pothole-Detection-for-shock-absorption-support.svg?style=for-the-badge
[forks-url]: https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/network/members
[stars-shield]: https://img.shields.io/github/stars/AlterraFa/Pothole-Detection-for-shock-absorption-support.svg?style=for-the-badge
[stars-url]: https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/stargazers
[issues-shield]: https://img.shields.io/github/issues/AlterraFa/Pothole-Detection-for-shock-absorption-support.svg?style=for-the-badge
[issues-url]: https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/issues
[license-shield]: https://img.shields.io/github/license/AlterraFa/Pothole-Detection-for-shock-absorption-support.svg?style=for-the-badge
[license-url]: https://github.com/AlterraFa/Pothole-Detection-for-shock-absorption-support/blob/master/LICENSE.txt
[product-screenshot]: Icon/IMAGE_Demo_UI.png
[Python]: https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54
[Python-url]: https://www.python.org/
