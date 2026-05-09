package com.sma.course.dto;

public record SummarizeCourseResponse(
        String fileId,
        String courseId,
        String summaryText,
        String generatedBy,
        String traceId
) {
}
