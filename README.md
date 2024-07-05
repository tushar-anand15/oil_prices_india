# Introduction

Daily fuel prices in India are reported in the form of a PDF on the PPAC [website](https://www.ppac.gov.in/) which is not amenable for data analysis. This project was created to convert the data into a usable format for analysis. Daily fuel prices are used to create a time-series interactive dashboard. Brent crude prices are also used to show trends over time. Typically, the difference between these prices is the tax levied by the government (both Central and State) as well as the profits of the dealer and refining charges. 


~~The app can be found [here](https://oil-prices-india.herokuapp.com/)~~ The link is not accessible anymore since Heroku is now paid.
It has the follwing charts:
- fuel prices (petrol and diesel) from June, 2017 to February, 2021
- comparison with Brent crude prices 
- percent change in fuel prices
- monthly average comparison of retail prices with Brent crude prices 


## Language
Created using Python 3.7.

## Set up

To run this project, clone the repository and run locally with
```
python3 app.py
```
To get the latest price data, run the following:
```
python3 preprocessing.py
```
Running the preprocessing file will update the daily price trend data. 

## Data sources:
- [PPAC website](https://www.ppac.gov.in/)
- Brent crude international oil price data
- USD-INR exchange rate from European Central Bank



## Issues
 Currently, crude price data is not integrated with the daily price data beyond February 22, 2021. Although the script downloads the latest PDF and prepares the daily price data, the visualisation does not update beyond this date. Other data sources such as consumption data also do not get updated. Will fix this in further commits.

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
