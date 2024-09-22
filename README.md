# Receipt-To-Split
This project is a web application that allows users to authenticate via PropelAuth, view their categorized expenses for the past month, and scan receipts to split costs with their group based on items purchased.

## Features
User Authentication:
The app is integrated with PropelAuth for user authentication. Users can sign up, log in, and securely access their account information.

Expense Dashboard:
View categorized expenses for the past month.
Categories include Housing, Transportation, Food, Entertainment, Healthcare, and more.
Each expense is organized by date, and users can visually explore their spending trends over the past 30 days.

Receipt Scanning & Cost Splitting:
Upload or scan a receipt to split costs.
Split the total receipt amount based on what each person purchased.
Easily assign specific items from the receipt to different people and calculate individual totals.

## Tech Stack
Frontend: React.js

Backend: Node.js / Express

Database: MongoDB

Authentication: PropelAuth

Receipt Scanning: Custom receipt OCR (Optical Character Recognition)

Visualization: Plotly for charts (or D3.js, Chart.js, etc.)

LLM: Cerebras API

##Team
Roshan Bellary, rbellary@seas.upenn.edu
Eshan Singhal, esinghal@seas.upenn.edu
Audhav Durai, audhav@wharton.upenn.edu
