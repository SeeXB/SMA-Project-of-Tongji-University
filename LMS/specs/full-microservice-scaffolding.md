# Canvas AI-Enhanced Subsystem Scaffolding

This document captures the six-core-microservice target structure derived from the assignment context.

## Architecture Notes

- Access Layer: Canvas-facing adapters and API gateway entry points expose coarse-grained APIs without changing Canvas core code.
- Business Service Layer: `course-service`, `assignment-service`, `qa-service`, and `moderation-service` own business orchestration and relational data.
- AI Capability Layer: `ai-gateway-service` centralizes synchronous/asynchronous model calls, while `rag-service` owns embedding persistence and retrieval.
- External Integration Layer: Canvas adapters, OpenAI-compatible providers, Kafka, PostgreSQL/MySQL, and Milvus are integrated through dedicated clients.
- Communication: REST is used for synchronous UX-critical operations; Kafka is reserved for long-running AI jobs and post-processing.
- Data Autonomy: each service owns its own database/schema and never reaches into another service's tables directly.
- Runtime note: the assignment target stack calls for Spring Boot 3.x business services. To keep the workspace runnable on the user's JDK 25 environment, the Java service skeletons in this repo are aligned to Spring Boot 4.0.5 even though the conceptual target remains Spring Boot 3.x.

## Service Trees

### Course Service
```text
course-service
├── pom.xml
└── src/main
    ├── java/com/sma/course
    │   ├── CourseServiceApplication.java
    │   ├── config/HttpClientConfig.java
    │   ├── controller/CourseController.java
    │   ├── dto
    │   │   ├── AiInferenceRequest.java
    │   │   ├── AiInferenceResponse.java
    │   │   ├── CanvasCourseContent.java
    │   │   ├── SummarizeCourseRequest.java
    │   │   └── SummarizeCourseResponse.java
    │   ├── integration
    │   │   ├── AiGatewayClient.java
    │   │   ├── CanvasAdapterClient.java
    │   │   └── TokenVerifier.java
    │   └── service
    │       ├── CourseSummarizationService.java
    │       └── impl/CourseSummarizationServiceImpl.java
    └── resources
        └── application.yml
```

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-actuator</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springdoc</groupId>
        <artifactId>springdoc-openapi-starter-webmvc-ui</artifactId>
        <version>2.6.0</version>
    </dependency>
</dependencies>
```

### Assignment Service
```text
assignment-service
├── pom.xml
└── src/main
    ├── java/com/sma/assignment
    │   ├── AssignmentServiceApplication.java
    │   ├── controller/
    │   └── service/
    └── resources
        └── application.yml
```

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

### QA Service
```text
qa-service
├── pom.xml
└── src/main
    ├── java/com/sma/qa
    │   ├── QaServiceApplication.java
    │   ├── controller/
    │   └── service/
    └── resources
        └── application.yml
```

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

### Moderation Service
```text
moderation-service
├── pom.xml
└── src/main
    ├── java/com/sma/moderation
    │   ├── ModerationServiceApplication.java
    │   ├── controller/
    │   └── service/
    └── resources
        └── application.yml
```

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-validation</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-data-jpa</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.kafka</groupId>
        <artifactId>spring-kafka</artifactId>
    </dependency>
    <dependency>
        <groupId>org.postgresql</groupId>
        <artifactId>postgresql</artifactId>
        <scope>runtime</scope>
    </dependency>
</dependencies>
```

### AI Gateway Service
```text
ai-gateway-service
├── requirements.txt
└── app
    ├── main.py
    ├── api/routes/inference.py
    ├── core/config.py
    ├── models/inference.py
    └── services/inference_service.py
```

```txt
fastapi==0.115.12
uvicorn[standard]==0.34.2
pydantic==2.11.3
pydantic-settings==2.8.1
httpx==0.28.1
langchain==0.3.23
langchain-openai==0.3.14
```

### RAG Service
```text
rag-service
├── requirements.txt
└── app
    ├── main.py
    ├── api/routes/
    ├── core/
    ├── models/
    └── services/
```

```txt
fastapi==0.115.12
uvicorn[standard]==0.34.2
pydantic==2.11.3
pydantic-settings==2.8.1
langchain==0.3.23
langchain-openai==0.3.14
pymilvus==2.5.6
httpx==0.28.1
```
