import time
import sys
import random
import requests
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from bs4 import BeautifulSoup
from termcolor import colored


class MyWindow(QWidget):
  def __init__(self, words: list[str]):
    """
    Initialize the main window of the application.

    Parameters
    ----------
    words : list[str]
      List of words to be used in the typing practice.

    Notes
    -----
    This function sets the size of the window, sets the title, and
    initializes the input box, question label, and result label. It
    also initializes the layout of the window and sets the current
    word to be shown in the question label.

    """
    super().__init__()
    self.resize(800, 400)
    self.setWindowTitle('Typing practice')

    self.inputbox = QLineEdit(self)
    self.inputbox.resize(500, 100)
    self.inputbox.returnPressed.connect(self.enter_text)

    self.question = QLabel("", self)
    self.question.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.question.setFont(QFont('Arial', 20))
    self.question.setStyleSheet('color: blue')
    self.question.resize(500, 100)

    self.result = QLabel("", self)
    self.result.setAlignment(Qt.AlignmentFlag.AlignCenter)
    self.result.setFont(QFont('Arial', 18))
    self.result.resize(500, 100)

    self.my_layout = QVBoxLayout(self)
    self.my_layout.addWidget(self.question)
    self.my_layout.addWidget(self.result)
    self.my_layout.addWidget(self.inputbox)
    self.my_layout.setContentsMargins(0, 0, 0, 0)
    self.setLayout(self.my_layout)

    self.words = words
    self.succ_cnt = 0
    self.cur_word = self.fetch_word()

  def enter_text(self):
    """
    Handles the user pressing enter in the input box.

    If the user input matches the current word, the word is marked as correct,
    the result label is set to green, and the correct words per second is computed
    and displayed. The next word is fetched and the process starts over.

    If the user input is 'finish practice', the window is closed and the number
    of words practiced is printed.

    If the user input is anything else, the result label is set to red and the
    text is set to 'wrong!'.
    """
    answer = self.inputbox.text().strip()
    self.inputbox.setText('')
    if answer == self.cur_word:
      self.succ_cnt += 1
      self.result.setStyleSheet('color: green')
      self.result.setText(f'correct! {len(self.cur_word) / (time.time() - self.start_time):.2f} char/s')
      self.cur_word = self.fetch_word()
    elif answer == 'finish practice':
      self.result.setStyleSheet('color: yellow')
      print(f'Practiced {self.succ_cnt} word{"s" if self.succ_cnt > 1 else ""}!')
      self.close()
    else:
      self.result.setStyleSheet('color: red')
      self.result.setText('wrong!')
      self.start_time = time.time()

  def fetch_word(self):
    """
    Fetch a random word from the list of words, set the text of the question
    label to the word and its translation, and set the start time of the current
    word.

    Returns
    -------
    str
      The current word.

    Notes
    -----
    This function is called when the user enters a word and presses enter or
    when the window is initialized.

    """
    rand_word = str(random.sample(self.words, 1)[0].strip())
    self.question.setText(f'{rand_word}  -  {crawl_translation(rand_word)}')
    self.start_time = time.time()
    return rand_word


def read_file(file):
  with open(file, 'r', encoding='utf8') as f:
    return f.readlines()


def crawl_translation(word: str) -> str:
  """
  Crawl the translation of a given word from Cambridge Dictionary.

  Parameters
  ----------
  word : str
    The word to be crawled.

  Returns
  -------
  str
    The crawled translation of the word. If no translation is found, it returns 'No translation found.'.

  Notes
  -----
  The user agent is set to a fake one to avoid being blocked by the server.
  """
  url_cand = [
    f'https://dictionary.cambridge.org/zht/%E8%A9%9E%E5%85%B8/%E8%8B%B1%E8%AA%9E-%E6%BC%A2%E8%AA%9E-%E7%B9%81%E9%AB%94/{word}',
  ]

  # crawl the chinese translation
  for url in url_cand:
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    target_class = soup.find(class_='dtrans')
    if target_class:
      return target_class.text
    else:
      return 'No translation found.'


def terminal_typing_practice(words: list[str]):
  """
  Practice typing in terminal.

  Parameters
  ----------
  words : list[str]
    The list of words to be practiced.

  Notes
  -----
  This function will enter an infinite loop and won't return until the user
  inputs 'finish practice' to exit. The user will be asked to input a word, and if the
  input is correct, the function will print the time spent on the word and
  ask for another word. If the input is incorrect, it will print 'wrong!'.
  """
  rand_word = str(random.sample(words, 1)[0].strip())
  succ_cnt = 0
  while True:
    # print the word
    print(colored(f'{rand_word}  -  {crawl_translation(rand_word)}', 'blue'))

    start_time = time.time()
    input_word = input()
    if input_word == 'finish practice':
      print(colored(f'Practiced {succ_cnt} word{'s' if succ_cnt > 1 else ''}!', 'yellow'))
      exit()
    elif input_word == rand_word:
      print(colored(f'correct! {len(rand_word) / (time.time() - start_time):.2f} char/s', 'green'))
      succ_cnt += 1
      rand_word = str(random.sample(words, 1)[0].strip())
    else:
      print(colored('wrong!', 'red'))


if __name__ == '__main__':
  words = read_file('Oxford 5000.txt')
  if input('Open GUI mode? (y/n): ') == 'y':
    app = QApplication(sys.argv)
    window = MyWindow(words)
    window.show()
    sys.exit(app.exec_())
  else:
    terminal_typing_practice(words=words)
