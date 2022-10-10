@echo off
title This is your first batch script!
cd C:\ZKREPORTING\
start streamlit run main.py --server.headless=true --global.developmentMode=false --server.port=8501
