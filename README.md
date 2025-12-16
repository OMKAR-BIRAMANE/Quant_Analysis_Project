# Real-Time Quant Analytics Dashboard
## Overview

This project implements a real-time quantitative analytics application that demonstrates an end-to-end workflow starting from live market data ingestion to statistical analysis and interactive visualization. The system is designed as a lightweight research and analytics tool similar to those used by quantitative trading and research teams working on statistical arbitrage, market microstructure analysis, and pair-based strategies.

The application connects to Binance WebSocket streams to receive live tick data, processes and aggregates this data into time-aligned series, computes multiple quantitative analytics, and exposes the results through an interactive dashboard with alerting and data export capabilities.

The emphasis of this project is on architectural clarity, analytical correctness, and extensibility, rather than production-scale throughput.

## System Design Summary

At a high level, the system follows a layered architecture:

A real-time ingestion layer consumes live tick data

A buffering mechanism decouples ingestion from storage

A persistence layer stores raw ticks for historical access

A resampling layer converts ticks into OHLCV bars

An analytics layer computes statistical signals

A presentation layer visualizes analytics and handles user interaction

Although the application runs as a single local process, each layer is intentionally designed so that it can be extracted into an independent microservice in a production environment.

## Data Ingestion

Market data is ingested from Binance using WebSocket connections. WebSockets were chosen over REST polling because market data is inherently event-driven and continuous. A push-based model ensures lower latency, avoids rate-limit issues, and prevents missed ticks during high activity periods.

The ingestion logic runs asynchronously to ensure that data collection never blocks downstream analytics or the user interface.

## Buffering and Storage

Incoming ticks are first placed into an in-memory buffer before being written to disk. This design decision serves two purposes:

It decouples the ingestion rate from the database write rate

It prevents database I/O from becoming a bottleneck during bursty market conditions

Ticks are periodically flushed in batches into a local SQLite database. SQLite was selected for its simplicity and zero-configuration setup, which is appropriate for a local analytical prototype.

To handle concurrent reads and writes safely, SQLite is configured using Write-Ahead Logging (WAL) mode, and database writes are serialized using explicit locking. This approach reflects real-world constraints of embedded databases and demonstrates awareness of concurrency limitations.

## Resampling and Time Alignment

Raw tick data is irregular and unsuitable for most statistical analyses. Therefore, ticks are resampled into fixed-interval OHLCV bars using Pandas.

The application supports multiple timeframes (such as 1-second and 1-minute bars). This step ensures that all downstream analytics operate on synchronized time series, which is critical for regression, correlation, and rolling window computations.

## Quantitative Analytics

The analytics layer is implemented as a set of pure, stateless functions that operate on resampled time series.

## Hedge Ratio (OLS Regression)

An Ordinary Least Squares (OLS) regression is used to estimate the hedge ratio between two instruments.

The hedge ratio (𝛽) represents the quantity of one asset required to hedge another and is a standard tool in pair-based analysis. OLS was chosen due to its interpretability and widespread acceptance in quantitative research.

Spread Construction

The spread represents the residual relationship between the two assets and forms the basis for mean-reversion analysis.

Rolling Z-Score

A rolling z-score is computed on the spread to quantify deviations from its recent mean:
$$
ZScore𝑡 = \frac{Spread𝑡 - \mu𝑡}{\sigma𝑡}
$$
where 𝜇𝑡 and 𝜎𝑡 are the rolling mean and standard deviation of the spread over a specified window.

Rolling windows are used to avoid lookahead bias and to allow statistics to adapt to changing market conditions. This signal is commonly used to identify overextended states in relative-value strategies.

Rolling Correlation

Rolling correlation between the two price series is computed to assess the stability of the relationship over time. This provides additional context for interpreting regression and spread behavior.

Alerts

The system includes a rule-based alert engine that evaluates analytics in near real time. Users can define thresholds (e.g., absolute z-score greater than a specified value), and alerts are triggered when these conditions are met.

Alerts are deliberately separated from the analytics logic to maintain modularity. An alert history is maintained in the dashboard for transparency and traceability.

## Visualization and User Interface

The frontend is built using Streamlit and Plotly. Streamlit enables rapid development of an interactive dashboard entirely in Python, while Plotly provides rich, interactive charts with zoom, pan, and hover capabilities.

The dashboard allows users to:

Select instruments and timeframes

Adjust rolling window parameters

View live-updating charts for prices, spreads, and z-scores

Monitor alerts in real time

Export processed analytics for offline analysis

The interface is designed to handle partial data availability gracefully, displaying warm-up states when insufficient data is available for rolling analytics.

## Data Export

Processed analytics can be exported as CSV files. The exported data includes aligned prices, spreads, and z-scores rather than raw tick data, reflecting typical research workflows. Export filenames dynamically reflect the selected instruments and timeframes.

## Challenges Encountered and Solutions

Several real-world issues were encountered during development:

Mixed timestamp formats from streaming data caused parsing errors. This was resolved by explicitly using ISO8601-compatible datetime parsing.

Database locking issues arose due to concurrent reads and writes in SQLite. These were addressed using WAL mode, serialized writes, and careful separation of ingestion and UI access paths.

Rolling window initialization errors occurred when analytics were computed before sufficient data was available. Guard conditions and warm-up states were added to prevent runtime failures.

Async event loop conflicts with Streamlit were resolved by running ingestion in a dedicated background thread with its own asyncio loop.

These challenges and their resolutions closely mirror issues encountered in real-time analytical systems.

## Local Setup and Execution

The application is designed for simple local execution. After creating and activating a Python virtual environment and installing dependencies, the entire system can be started with a single command:

streamlit run app.py


On startup, the application automatically begins ingesting live market data and enables analytics as data becomes available.

## ChatGPT Usage 

ChatGPT was used as a development aid for architectural reasoning, code structuring guidance, debugging assistance, and documentation refinement. All generated suggestions were manually reviewed, adapted, and tested. Final design decisions and validation were performed independently.

## Scalability Considerations

While this implementation runs locally as a layered monolith, the architecture maps directly to a scalable microservice design. In a production setting, ingestion, analytics, alerts, and storage could be deployed as independent services connected via a streaming backbone such as Kafka, with a time-series database replacing SQLite.

## Conclusion

This project demonstrates the design and implementation of a complete real-time quantitative analytics pipeline. It balances simplicity with realism, emphasizing correct statistical methodology, modular system design, and clear communication. The resulting application serves as a functional prototype that could evolve into a larger analytics platform with minimal architectural changes.
