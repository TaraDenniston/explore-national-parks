# Database Schema for Explore National Parks


```mermaid
erDiagram
    USERS ||--o{ FAVORITES : ""
    USERS ||--o{ NOTES : ""
    USERS {
        integer id PK
        string(50) email
        text password
        string(30) first_name
        string(30) last_name
    }
    PARKS ||--o{ FAVORITES : ""
    PARKS ||--o{ NOTES : ""
    PARKS {
        string(10) park_code PK
        string(100) full_name
        text description
        text image_url
        text image_alt
    }
    FAVORITES {
        integer id PK
        string(10) park_code FK
        integer user_id FK
    }
    NOTES {
        integer id PK
        string(10) park_code FK
        integer user_id FK
        text text
    }
```



