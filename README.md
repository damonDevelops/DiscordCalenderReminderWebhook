
# Daily Google Calendar Event Reminder

This project automates the process of fetching daily events from multiple Google Calendars and sends a summary notification to a designated Discord channel. It's designed to help users stay organized by providing timely reminders of their daily schedules.

## Features

- Fetches events from multiple Google Calendars.
- Categorizes events based on different calendars (e.g., personal, partner, shared).
- Sends a daily summary notification to a Discord channel with events neatly organized and labeled.

## Setup Instructions

### Prerequisites

1. **Python 3.12+** installed on your machine.
2. A Google Cloud Project with the Calendar API enabled.
3. Credentials for Google API access (`credentials.json`).
4. A Discord Webhook URL for sending notifications.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/damonDevelops/Daily-Google-Calendar-Discord-Reminder
   cd Daily-Google-Calendar-Discord-Reminder
   ```

2. **Create and activate a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scriptsctivate`
   ```

3. **Install the required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Add environment variables:**
   * Create a `.env` file in the root directory of your project and add the following variables:
     ```
     DISCORD_WEBHOOK_URL=your-discord-webhook-url
     CHANNEL_ID=your-channel-id
     ```

5. **Obtain Google API credentials:**
   * Download the `credentials.json` file from your Google Cloud Project.
   * Place it in the root directory of your project.

### Usage
To run the script locally:
```bash
functions-framework --target test_function
```
To send the daily reminder:
   * The file if run successfully will send the message to a discord channel
   * To leave it autonomously, you must deploy it to Cloud Functions

### Deployment on Google Cloud Functions
1. **Deploy the function:**
   * Through CLI or online console, create an application and Cloud Function
   * Test the function thoroughly (I did with unauthorized access before switching this off)
   * Note: this process can be frustrating and tricky, I suggest consulting GCP docs and discord docs

2. **Set up Cloud Scheduler to trigger the function daily:**
   * Use the GCP Console to create a Cloud Scheduler job.
   * Schedule the job with the desired frequency (e.g., every day at 7 PM).

### Contributing
Contributions are welcome! Please submit a pull request or open an issue for any changes or additions you would like to see.

### License
This project is licensed under the MIT License - see the LICENSE file for details.

Thanks to the Google API Python Client team for providing the tools to interact with Google services.
