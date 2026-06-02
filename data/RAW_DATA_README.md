# About the Dataset
To simulate passenger flight information, the [airline_delays](https://www.kaggle.com/datasets/ulrikthygepedersen/airlines-delay) Kaggle dataset is used. It features binary labels to predict whether a flight is delayed.

## Column Definitions

| Column | Type | Description | Format / Example |
| :--- | :--- | :--- | :--- |
| **Flight** | Integer | Unique flight number identifier (not unique per row). | `26`, `2432` |
| **Time** | Integer | Departure time in minutes from the start of the day. | `610` $\rightarrow$ 10:10 (10h 10m) |
| **Length** | Integer | Flight duration in minutes. | `375` $\rightarrow$ 6h 15m |
| **Airline** | String | Two-letter IATA airline code. | `DL`, `WN`, `AA` |
| **AirportFrom**| String | Three-letter IATA code for the departure US airport.| `LAX`, `ATL` |
| **AirportTo** | String | Three-letter IATA code for the destination US airport.| `ORD`, `JFK` |
| **DayOfWeek** | Integer | Day of the week (1 = Monday, 7 = Sunday). | `1` (Mon) to `7` (Sun) |
| **Class** | Integer | Target binary label for flight delay status. | `0` = On Time, `1` = Delayed |

### Technical Notes
* Time Conversion: To convert `Time` and `Length` to a standard format, use floor division (`//`) for hours and modulo (`%`) for minutes.
  * *Departure Time:* `610 // 60` = 10 hours; `610 % 60` = 10 minutes $\rightarrow$ 10:10
  * *Flight Length:* `375 // 60` = 6 hours; `375 % 60` = 15 minutes $\rightarrow$ 6h 15m.
* Flight IDs: The `Flight` column contains categorical values; multiple rows can share the same flight ID representing different dates or times.