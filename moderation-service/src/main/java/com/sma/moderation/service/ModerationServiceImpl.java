package com.sma.moderation.service;

import com.sma.moderation.dto.ModerationFileRequest;
import com.sma.moderation.dto.ModerationFileResponse;
import com.sma.moderation.dto.ModerationTextRequest;
import com.sma.moderation.dto.ModerationTextResponse;
import java.util.Map;
import org.springframework.stereotype.Service;

@Service
public class ModerationServiceImpl implements ModerationService {

    @Override
    public ModerationTextResponse moderateText(ModerationTextRequest request) {
        boolean flagged = request.text().toLowerCase().contains("banned");
        return new ModerationTextResponse(
                flagged,
                Map.of("toxicity", flagged ? 0.91 : 0.12, "self_harm", 0.01),
                flagged ? "Contains banned keyword placeholder." : "No significant issue detected."
        );
    }

    @Override
    public ModerationFileResponse moderateFile(ModerationFileRequest request) {
        boolean flagged = request.extractedText() != null && request.extractedText().toLowerCase().contains("banned");
        return new ModerationFileResponse(
                request.fileId(),
                flagged,
                flagged ? "Extracted content contains flagged language." : "File passed moderation."
        );
    }
}
