package com.sma.moderation.controller;

import com.sma.moderation.dto.ModerationFileRequest;
import com.sma.moderation.dto.ModerationFileResponse;
import com.sma.moderation.dto.ModerationTextRequest;
import com.sma.moderation.dto.ModerationTextResponse;
import com.sma.moderation.service.ModerationService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/moderation")
public class ModerationController {

    private final ModerationService moderationService;

    public ModerationController(ModerationService moderationService) {
        this.moderationService = moderationService;
    }

    @PostMapping("/text")
    public ResponseEntity<ModerationTextResponse> moderateText(@Valid @RequestBody ModerationTextRequest request) {
        return ResponseEntity.ok(moderationService.moderateText(request));
    }

    @PostMapping("/file")
    public ResponseEntity<ModerationFileResponse> moderateFile(@Valid @RequestBody ModerationFileRequest request) {
        return ResponseEntity.ok(moderationService.moderateFile(request));
    }
}
