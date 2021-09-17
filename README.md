<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/github_username/repo_name">
    <img src="images/SSC_logo.png" alt="Logo" width="400" height="400">
  </a>

  <h3 align="center">Sac SSC Scheduler Application </h3>

  <p align="center">
    Software Solution for the Sacramento Senior Safety Collaborative Escort Program.
    <br />
    <br />
    ·
    <a href="https://github.com/justin-curtis-lu/ACC-Scheduler/issues">Report Bug</a>
    ·
    <a href="https://github.com/justin-curtis-lu/ACC-Scheduler/issues">Request Feature</a>
  </p>
</p>



<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgements">Acknowledgements</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project


<img src="images/console.jpg" alt="Console" width="750" height="400">


### Built With

* [Django](https://www.djangoproject.com/)
* [SQLite](https://www.sqlite.org/index.html)
* [Bootstrap](https://getbootstrap.com/)
* [DateTimePicker plugin](https://xdsoft.net/jqplugins/datetimepicker/)
* [Twilio API](https://www.twilio.com/docs/usage/api)
* [Galaxy Digital API](http://api2.galaxydigital.com/volunteer/docs/)



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

Twilio Account - (Using the Twilio API will require an Account SID and Auth Token)

Galaxy Digital Account - (Utilizing the volunteer management service will require an API Key)

Gmail Account - (For sending Emails, will require the email user and password)

Python 3.8

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/justin-curtis-lu/ACC-Scheduler.git
   ```
2. Install Python packages
   ```sh
   pip install -r requirements.txt
   ```
3. Create a .env file in the root. Observe the values extracted from enviornment variables in settings.py and set the associated values in the .env file.
4. Apply Migrations
   ```sh
   python manage.py migrate
   ```
5. Run the application
   ```sh
   python manage.py runserver
   ```

<!-- USAGE EXAMPLES -->
## Usage

This application serves as a specific solution to handle scheduling for the Sac SSC Escort Program. It's main goals serve as an admin interface that allows for scheduling between participants and volunteers for 1 to 1 appointments. It also collects availability using surveys sent through SMS and Gmail. Although this application utilizes the [Galaxy Digital API](https://www.galaxydigital.com/) to sync with ACC Senior Services data, this feature can be removed, and manual volunteers and participants can be added. We recommend using Digital Ocean for deployment.


<!-- ROADMAP -->
## Roadmap

See the [open issues](https://github.com/justin-curtis-lu/ACC-Scheduler/issues) for a list of proposed features (and known issues).



<!-- CONTRIBUTING -->
## Contributing


1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* Larry Jacobs
* [ACC Senior Services](https://www.accsv.org/)





<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/justin-curtis-lu/ACC-Scheduler.svg?style=for-the-badge
[contributors-url]: https://github.com/justin-curtis-lu/ACC-Scheduler/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/justin-curtis-lu/ACC-Scheduler.svg?style=for-the-badge
[forks-url]: https://github.com/justin-curtis-lu/ACC-Scheduler/network/members
[stars-shield]: https://img.shields.io/github/stars/justin-curtis-lu/ACC-Scheduler.svg?style=for-the-badge
[stars-url]: https://github.com/justin-curtis-lu/ACC-Scheduler/stargazers
[issues-shield]: https://img.shields.io/github/issues/justin-curtis-lu/ACC-Scheduler.svg?style=for-the-badge
[issues-url]: https://github.com/justin-curtis-lu/ACC-Scheduler/issues
[license-shield]: https://img.shields.io/github/license/justin-curtis-lu/ACC-Scheduler.svg?style=for-the-badge
[license-url]: https://github.com/justin-curtis-lu/ACC-Scheduler/master/MIT-License
