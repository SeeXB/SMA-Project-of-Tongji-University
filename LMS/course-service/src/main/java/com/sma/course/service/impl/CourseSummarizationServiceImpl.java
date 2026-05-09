package com.sma.course.service.impl;

import com.sma.course.dto.AiInferenceRequest;
import com.sma.course.dto.AiInferenceResponse;
import com.sma.course.dto.CanvasCourseContent;
import com.sma.course.dto.GenerateQuizRequest;
import com.sma.course.dto.GenerateQuizResponse;
import com.sma.course.dto.QuizQuestion;
import com.sma.course.dto.SummarizeCourseRequest;
import com.sma.course.dto.SummarizeCourseResponse;
import com.sma.course.integration.AiGatewayClient;
import com.sma.course.integration.CanvasAdapterClient;
import com.sma.course.integration.TokenVerifier;
import com.sma.course.service.CourseSummarizationService;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import org.springframework.stereotype.Service;

@Service
public class CourseSummarizationServiceImpl implements CourseSummarizationService {

    private final TokenVerifier tokenVerifier;
    private final CanvasAdapterClient canvasAdapterClient;
    private final AiGatewayClient aiGatewayClient;

    public CourseSummarizationServiceImpl(
            TokenVerifier tokenVerifier,
            CanvasAdapterClient canvasAdapterClient,
            AiGatewayClient aiGatewayClient
    ) {
        this.tokenVerifier = tokenVerifier;
        this.canvasAdapterClient = canvasAdapterClient;
        this.aiGatewayClient = aiGatewayClient;
    }

    @Override
    public SummarizeCourseResponse summarizeSlides(SummarizeCourseRequest request) {
        tokenVerifier.verify(request.accessToken(), request.userId());

        CanvasCourseContent courseContent = canvasAdapterClient.fetchSlideContent(
                request.courseId(),
                request.fileId()
        );

        String traceId = UUID.randomUUID().toString();
        String prompt = """
                Summarize the following course slides for a university student.
                Focus on learning objectives, key concepts, and any action items.
                Preferred language: %s

                Slide title: %s
                Slide content:
                %s
                """.formatted(
                request.preferredLanguage() == null || request.preferredLanguage().isBlank()
                        ? "English"
                        : request.preferredLanguage(),
                courseContent.title(),
                courseContent.rawText()
        );

        AiInferenceResponse inferenceResponse = aiGatewayClient.inferSync(
                new AiInferenceRequest(
                        "slide-summary",
                        prompt,
                        traceId,
                        request.userId(),
                        Map.of(
                                "courseId", request.courseId(),
                                "fileId", request.fileId()
                        )
                )
        );

        return new SummarizeCourseResponse(
                request.fileId(),
                request.courseId(),
                inferenceResponse.outputText(),
                inferenceResponse.provider() + ":" + inferenceResponse.model(),
                inferenceResponse.traceId()
        );
    }

    @Override
    public GenerateQuizResponse generateQuiz(GenerateQuizRequest request) {
        tokenVerifier.verify(request.accessToken(), request.userId());

        CanvasCourseContent courseContent = canvasAdapterClient.fetchSlideContent(
                request.courseId(),
                request.fileId()
        );

        String traceId = UUID.randomUUID().toString();
        String prompt = """
                Create %d multiple-choice quiz questions from the following course material.
                Difficulty: %s
                Keep questions concise and suitable for undergraduate students.

                Course material:
                %s
                """.formatted(
                request.questionCount(),
                request.difficulty() == null || request.difficulty().isBlank() ? "medium" : request.difficulty(),
                courseContent.rawText()
        );

        AiInferenceResponse inferenceResponse = aiGatewayClient.inferSync(
                new AiInferenceRequest(
                        "quiz-generation",
                        prompt,
                        traceId,
                        request.userId(),
                        Map.of(
                                "courseId", request.courseId(),
                                "fileId", request.fileId()
                        )
                )
        );

        List<QuizQuestion> questions = List.of(
                new QuizQuestion(
                        UUID.randomUUID().toString(),
                        "What is a bounded context in Domain-Driven Design?",
                        List.of(
                                "A deployment script",
                                "A clear model boundary for a specific domain area",
                                "A database backup strategy",
                                "A browser sandbox"
                        ),
                        "A clear model boundary for a specific domain area",
                        "Bounded contexts separate different business models to reduce coupling."
                ),
                new QuizQuestion(
                        UUID.randomUUID().toString(),
                        "Why are aggregates used in DDD?",
                        List.of(
                                "To manage consistency boundaries",
                                "To replace message queues",
                                "To configure SSL certificates",
                                "To render dashboards"
                        ),
                        "To manage consistency boundaries",
                        "Aggregates group related domain objects that should stay consistent together."
                )
        );

        return new GenerateQuizResponse(
                UUID.randomUUID().toString(),
                request.courseId(),
                questions.subList(0, Math.min(request.questionCount(), questions.size())),
                inferenceResponse.outputText(),
                inferenceResponse.traceId()
        );
    }
}
