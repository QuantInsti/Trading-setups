## Introduction

This folder contains a working trading setup you can use to learn how to trade in the financial markets algorithmically. The setup can be used to trade any forex asset using the Interactive Brokers API. 

-----

## Licensed under the Apache License, Version 2.0 (the "License")
- Copyright 2025 QuantInsti Quantitative Learnings Pvt Ltd.
- You may not use this file except in compliance with the License.
- You may obtain a copy of the License at [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)
- Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

-----

## Disclaimer
**This trading setup and its strategy are just a template and should not be used for live trading without appropriate backtesting and tweaking of the strategy parameters.**

1. Cautionary note <a id='one'></a>
    - Trading is not appropriate for all investors and carries a significant risk.
    - Markets are unpredictable, and past performance does not guarantee future outcomes.
    - The trading setup and the strategy that are provided here are merely meant to be educational; they are not meant to be regarded as specific investing advice.
2. Limitations and assumptions <a id='two'></a>
    - Trading experience: The trading setup and the strategy provided here are predicated on the supposition that traders possess the necessary expertise to comprehend the risks involved and modify both according to their unique risk tolerance and preferences.
    - Risk capital: Trading should only be done with risk capital, and only people who have enough of it should think about trading. It is not advisable to trade with capital that can affect your way of life or financial commitments.
    - Market volatility:  The trading setups and strategies provided here are contingent upon the state of the market and may not yield anticipated results during periods of high market volatility or atypical occurrences.
    - No promises: Trading losses are possible, and neither success nor profit are certain.
3. Additional notes  <a id='three'></a>
    - Before implementing any trading strategy, you must conduct independent research and due diligence.
    - Trading involves emotions, and managing your emotions and risk tolerance is crucial.
4. Accountability
    - By utilizing these trading setups and their strategies detailed in this repository, you agree that:
        - You have read and understood the disclaimer and points [1](#one), [2](#two), and [3](#three).
        - You assume full accountability for your trading and investing decisions.
        - You alone will bear responsibility for any losses incurred if you employ this trading setup and approach.

## Table of contents
1. [Author](#author)
2. [Setup details](#details)
3. [Read the documentation](#documentation)
4. [Ask for help](#help)
5. [QuantInsti Learning Products](#products)
6. [Quick start](#start)

<a id='author'></a>
## Author
- [José Carlos Gonzáles Tanaka](https://www.linkedin.com/in/jose-carlos-gonzales-tanaka/)
- QuantInsti's EPAT content team is responsible for maintaining and contributing to this project.

<a id='details'></a>
## Setup details
- The trading setup allows you to trade any forex asset available in Interactive Brokers.
- You can only trade forex assets with this trading setup.
- It uses the stable version of the Interactive Brokers API (IB API).
- It can be used with the TWS platform or the IB Gateway as long as the trader installs the stable versions of each.
- The setup is packaged as a Python library and is installable with one single code line.
- You can use the trading setup package with any operating system, and from any country or timezone.
- There are two files apart from the trading setup package: The 'main' file and the 'strategy_file' file. You can use the former to run the whole trading setup. You can change the latter at your discretion. The latter contains all the relevant functions you can tweak to use your strategy.
- The package has 7 modules, see:
    - create_database.py (to create the trading Excel file to save all the setup output)
    - engine.py (the main loop functions to run the setup for each period)
    - ib_functions.py (IB-based customized functions to be used for the below modules)
    - setup.py (the setup class)
    - setup_for_download_data.py (the setup class and functions to download the historical minute data)
    - setup_functions.py (the customized functions to be used by the setup class)
    - trading_functions.py (the functions to be used by the above modules)
- The setup is ready to be tested or modified to meet your needs.

<a id='documentation'></a>
## Read the documentation
You can use this setup only for forex assets with an Interactive Brokers API. 
- To test the trading setup quickly, please read: “Start_here_documentation”.
- To use a customized strategy, please read: “Strategy_documentation”.
- To learn more about the trading setup, please read: “The_trading_setup_references”.
- Whenever you download again the setup or you want to modify the source code and run the setup, please read: “Develper_documentation”.

<a id='help'></a>
## Ask for help
In case of questions, please write to:
- Your support manager (if you’re a present EPAT student)
- The alumni team (if you’re a past EPAT student and an alumnus)

<a id='products'></a>
## QuantInsti Learning Products
- The trading setup is built based on [EPAT](https://www.quantinsti.com/epat?utm_source=github&utm_medium=referral&utm_campaign=trading-setups&utm_content=ib-forex-setup-readme) content
- To learn more about our products visit [QuantInsti](https://www.quantinsti.com/?utm_source=github&utm_medium=referral&utm_campaign=trading-setups&utm_content=ib-forex-setup-readme)

<a id='start'></a>
## Quick start
1. Download the "dist" and the "samples" folders, and save them in the “..path_to/Jts/setup" folder.
2. Open an Anaconda terminal (or a terminal in Linux or Mac), then type (wait until each command is completely run):

    - conda create --name setup_env python=3.12
   
      ![image01](res/image01.png)
      
    - conda activate setup_env
      
      ![image02](res/image02.png)
      
    - conda install spyder
      ![image03](res/image03.png)
      
    - cd 'path_to/Jts'
      ![image04](res/image04.png)
    - pip install ib_forex_setup/dist/qi_forex_setup-1.0.0-py3-none-any.whl
      ![image05](res/image05.png)

4. Since you have already installed the IB API in 'path_to/Jts/tws_api'. Let's install it in our 'setup_env" environment. Type:
    - cd 'path_to/Jts/tws_api/source/pythonclient'
      ![image06](res/image06.png)
    - python setup.py install
      ![image07](res/image07.png)
    - cd C:\Jts
      ![image08](res/image08.png)
    - spyder
      ![image09](res/image09.png)
5. Once Spyder is opened, select as main folder the "setup" folder and open the "main.py" 
6. Modify the inputs as per your trading requirements.
7. Run the file, and ...

# Go live algo trading!
