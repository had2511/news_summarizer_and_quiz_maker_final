🧠 About the Project

Real-Time News Summarizer and Quiz Maker is an AI-powered web application designed to make learning from current news both efficient and engaging.
The system automatically fetches the latest news from reliable sources in real time, summarizes them using a fine-tuned BART model, and generates interactive quizzes through the Gemini API.

Our goal is to bridge the gap between information overload and effective learning — helping users grasp the key points of daily news while reinforcing their understanding through quizzes.


here is the gudie to how to impliment this in your system:
1) run the code fine_tuned_bart_large_cnn.ipynb in kaggle. download the folder containing the model. and save the folder inside a folder.
2) copy the codes app.py, news_fetcher.py, summarizer.py, and quiz_generator.py into the same folder where the model folder is saved.
3) install the following dependencies in your ide(vs code).
      pip install streamlit transformers torch requests
      pip install generative.ai
4) also save your api keys in .ev file
5) streamlit run app.py

after that your ui is ready.
