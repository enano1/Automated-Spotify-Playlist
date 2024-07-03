# Automated Spotify Playlist with Google Authentication

## Overview

This innovative Flask application, leverages Google OAuth 2.0 for secure user authentication and integrates Spotify's API to create and manage playlists based on individual words or sentences provided by users. It also utilizes the Dog CEO's Dog API to fetch and set random dog images as unique playlist covers, adding a visual appeal to the playlists.

## Features

- **Google Authentication**: Utilizes Google OAuth 2.0 to securely authenticate users, ensuring access control and data protection.
- **Spotify Playlist Management**: Automatically generates unique Spotify playlists from user-inputted text, utilizing Spotify's API for playlist generation.
- **Dynamic Playlist Covers**: Incorporates random dog images from the Dog CEO's Dog API as playlist covers.
- **Interactive Web Interface**: Provides a user-friendly interface for logging in, creating playlists, and managing playlist content.

## Video Demonstration

[Watch the video demonstration of the application](https://youtu.be/f4swMqsFVGQ)

## Technical Details

### HTTP Methods
- **GET Requests** (Read): Used for retrieving data like user profiles and random images without changing the server state.
- **PUT Requests** (Update): Used to update existing resources, or to create new resources at a specified, known URL.
- **POST Requests** (Create): Used to submit data to create or modify playlists on Spotify, with the server providing the new URL.

### API Integration
- **Spotify API**: Manages authentication, search, and playlist operations.
- **Google API**: Ensures secure user authentication and session management.
- **Dog CEO's Dog API**: Provides random images for playlist covers.

## Setup Instructions

### Prerequisites
- Python 3.x
- pip (Python package manager)

### Installation
1. Clone the repository.
2. Navigate to the project directory.
3. Run `pip install -r requirements.txt`.

### Environment Setup
- Create a `.env` file in the root directory.
- Include `clientsecret.json` for Firebase with your Google API secret key.
- Obtain and set the Spotify API key.

## Usage

After setting up the environment and dependencies, run the application and log in using Google. Input text to generate playlists, which will automatically receive unique covers from the Dog CEO's API. Access and manage these playlists through the provided Spotify link.

## Contribution Guidelines

Contributions are welcome. Please follow the standard git workflow:
1. Fork the project.
2. Create a feature branch.
3. Commit your enhancements.
4. Push to the branch.
5. Submit a pull request.

## Support

For queries or assistance, contact the team members via their GitHub profiles or open an issue on the GitHub repository page.

## Important Note

All APIs have been deactivated, and you will need to generate your own Spotify Development API key and Google Firebase API key (Client and Secret) to run the project effectively.

## Documentation

For more detailed documentation, refer to the `documentation` folder in the repository.
