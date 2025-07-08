# AutoMedAI Autonomous

AutoMedAI Autonomous is a modular, agent-based system designed for medical diagnosis and triage. It coordinates multiple specialist agents to synthesize findings and provide recommendations for telemedicine scenarios.

## Features
- Central coordinating agent for managing specialist agents
- Mock specialist agents for various medical domains (Cardio, Neuro, Ortho, etc.)
- Rule-based aggregation and triage recommendations (mock phase)
- Designed for easy extension with LLMs and real specialist logic

## Getting Started
1. Clone the repository:
   ```sh
   git clone https://github.com/tusharn12/AutoMedAI-Autonomous.git
   cd AutoMedAI-Autonomous
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Run the main application:
   ```sh
   python app/main.py
   ```

## Project Structure
- `app/agents/` - Specialist and central agent logic
- `app/core/` - Core utilities and logging
- `app/main.py` - Entry point for the application

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
This project is for demonstration and research purposes only.