package com.sma.course.integration;

import com.sma.course.dto.CanvasCourseContent;
import org.springframework.stereotype.Component;

@Component
public class CanvasAdapterClient {

    public CanvasCourseContent fetchSlideContent(String courseId, String fileId) {
        String rawText = """
                Week 4 covers Domain-Driven Design foundations.
                The slides explain bounded contexts, aggregates, repositories, and anti-corruption layers.
                Students should understand why business capabilities map naturally to microservices.
                """;

        return new CanvasCourseContent(
                fileId,
                "Course " + courseId + " Slide Deck",
                rawText
        );
    }
}
