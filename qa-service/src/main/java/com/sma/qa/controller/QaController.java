package com.sma.qa.controller;

import com.sma.qa.dto.QaAskRequest;
import com.sma.qa.dto.QaAskResponse;
import com.sma.qa.dto.QaHistoryDetailResponse;
import com.sma.qa.dto.QaHistoryListResponse;
import com.sma.qa.service.QaService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/qa")
public class QaController {

    private final QaService qaService;

    public QaController(QaService qaService) {
        this.qaService = qaService;
    }

    @PostMapping("/ask")
    public ResponseEntity<QaAskResponse> ask(@Valid @RequestBody QaAskRequest request) {
        return ResponseEntity.ok(qaService.ask(request));
    }

    @GetMapping("/history-list")
    public ResponseEntity<QaHistoryListResponse> historyList(
            @RequestParam String userId,
            @RequestParam(required = false) String courseId
    ) {
        return ResponseEntity.ok(qaService.listHistory(userId, courseId));
    }

    @GetMapping("/history/{historyId}")
    public ResponseEntity<QaHistoryDetailResponse> historyDetail(@PathVariable String historyId) {
        return ResponseEntity.ok(qaService.getHistory(historyId));
    }
}
