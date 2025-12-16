# **Real-Time Quant Analytics Application**
1. ## Objective

The objective of this project is to design and implement a small but complete analytical application that demonstrates the ability to work end-to-end, starting from real-time market data ingestion to quantitative analytics and interactive visualization.

The application consumes live tick data from Binance WebSocket streams, processes and samples this data into time-aligned series, computes key quantitative analytics commonly used in statistical arbitrage and market research, and presents the results through an interactive dashboard.

The focus of this project is analytical reasoning, system design, and clarity of communication, rather than production-scale deployment.

2. ## Context

This application is designed as a helper analytics tool for traders and researchers at a quantitative trading firm operating across:

Cash and derivatives markets

Statistical arbitrage strategies

Risk premia harvesting

Market-making and micro-alpha research

The analytics implemented are representative of pair analysis and mean-reversion research workflows commonly used in such environments.

3. ## Workflow Overview
3.1 ### Data Source

Live tick data is streamed from Binance Futures WebSocket

Each tick contains:

Timestamp
Symbol
Price
Quantity (size)

WebSockets were chosen instead of REST polling to ensure low-latency, event-driven ingestion, which is critical for real-time analytics.

3.2 ### Data Handling & Storage

The data handling pipeline follows this sequence:

Asynchronous WebSocket ingestion

In-memory buffering of ticks

Batch persistence into a local SQLite database

Resampling into selectable timeframes (1s, 1m)

Design Rationale

Writing each tick directly to the database would create an I/O bottleneck.

The in-memory buffer decouples ingestion speed from storage speed.

SQLite was chosen for simplicity and zero-configuration local persistence.

This design mirrors industry patterns such as Kafka → Database sinks, but in a simplified local form.

3.3 ### Sampling & Resampling

Tick data is converted into OHLCV bars using Pandas resampling:

Supported timeframes: 1s, 1m

Open/High/Low/Close are computed from tick prices

Volume is aggregated from trade quantities

Resampling is a critical step because:

Most statistical analytics require aligned time series

Tick data is irregular and noisy

4. ## Analytics Implemented

The analytics layer is implemented as pure, stateless functions, separated from ingestion and visualization.

4.1 ### Price Statistics

Close prices extracted from resampled bars

Used as inputs to all downstream analytics

4.2 Hedge Ratio (OLS Regression)

The hedge ratio is computed using Ordinary Least Squares (OLS) regression:

𝐴
𝑡
=
𝛼
+
𝛽
𝐵
𝑡
+
𝜖
𝑡
A
t
	​

=α+βB
t
	​

+ϵ
t
	​


Where:

𝐴
𝑡
A
t
	​

 and 
𝐵
𝑡
B
t
	​

 are aligned close prices

𝛽
β represents the hedge ratio

OLS was chosen because it is:

Interpretable

Industry-standard for pair relationships

More appropriate than correlation for hedge estimation

4.3 Spread

The spread is computed as:

Spread
𝑡
=
𝐴
𝑡
−
𝛽
𝐵
𝑡
Spread
t
	​

=A
t
	​

−βB
t
	​


The spread represents the residual relationship between the two assets and is a common input to mean-reversion strategies.

4.4 Rolling Z-Score

A rolling z-score is computed on the spread:

𝑍
𝑡
=
Spread
𝑡
−
𝜇
𝑡
𝜎
𝑡
Z
t
	​

=
σ
t
	​

Spread
t
	​

−μ
t
	​

	​


Rolling windows are used to avoid lookahead bias

This allows the statistics to adapt to changing market conditions

4.5 Rolling Correlation

Rolling correlation between the two assets is computed to:

Monitor pair stability

Validate regression assumptions over time

4.6 Alerts

The system supports user-defined rule-based alerts:

Alerts are triggered when |z-score| exceeds a configurable threshold

Alerts are evaluated on live-updating analytics

An alert history table is maintained in the dashboard

5. Live Analytics Behavior

Ingestion runs continuously in the background

Storage and resampling occur incrementally

Analytics become available only after sufficient data is collected

During warm-up periods, the UI displays informative messages instead of failing

This reflects real-world trading systems where analytics must handle partial data availability gracefully.

6. Frontend & Visualization

The frontend is implemented using Streamlit with Plotly charts.

Features:

Interactive price charts

Spread and z-score plots

Zoom, pan, and hover support

Sidebar controls for:

Symbol selection

Timeframe

Rolling window

Lookback period

Alert thresholds

CSV export of processed analytics

Streamlit was chosen to enable rapid prototyping while keeping all logic in Python.

7. Data Export

Users can download a CSV file containing:

Prices of both instruments

Spread

Z-score

The exported data is:

Time-aligned

Derived from processed analytics (not raw ticks)

Named dynamically based on symbols and timeframe

8. Problems Faced & Solutions
8.1 Mixed Timestamp Formats

Problem:
Streaming data produced timestamps with and without microseconds, causing Pandas parsing errors.

Solution:
Used pd.to_datetime(..., format="ISO8601") to robustly handle mixed formats.

8.2 Database Write Bottleneck

Problem:
Writing each tick individually degraded performance.

Solution:
Introduced an in-memory buffer with periodic batch writes to the database.

8.3 Rolling Window Initialization Errors

Problem:
Rolling analytics caused index errors when insufficient data was available.

Solution:
Added explicit warm-up handling and guarded all rolling computations.

8.4 Async Event Loop Conflicts

Problem:
Async WebSocket ingestion conflicted with Streamlit’s execution model.

Solution:
Moved ingestion into a background thread with its own asyncio event loop.

9. Architecture & Design Considerations

The current implementation uses a layered monolithic architecture for simplicity, but each layer maps directly to a future microservice:

Layer	Future Microservice
Ingestion	Market Data Service
Buffer	Kafka / Redis Streams
Storage	Time-Series Database
Analytics	Signal Engine
Alerts	Rule Engine
Frontend	Web Dashboard

This ensures:

Loose coupling

Extensibility

Minimal rework for scaling

10. Setup Instructions (Local Execution)
Step 1: Create Virtual Environment
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate

Step 2: Install Dependencies
pip install -r requirements.txt

Step 3: Run Application
streamlit run app.py


The application will automatically:

Start WebSocket ingestion

Persist data

Enable analytics as data becomes available

11. ChatGPT Usage Transparency

ChatGPT was used for:

Architectural structuring

Code organization guidance

Debugging assistance

Documentation drafting

All generated suggestions were manually reviewed, adapted, and validated.
Final design decisions, testing, and correctness checks were performed independently.

12. Deliverables Included

Runnable application (single-command execution)

README.md (this document)

Architecture diagram (.drawio + exported image)

Modular and extensible codebase

13. Conclusion

This project demonstrates:

End-to-end real-time analytics

Correct quantitative methodology

Thoughtful system design

Clear trade-off reasoning

It is intended as a prototype analytics stack that could evolve into a larger, production-grade system while maintaining clarity and simplicity.