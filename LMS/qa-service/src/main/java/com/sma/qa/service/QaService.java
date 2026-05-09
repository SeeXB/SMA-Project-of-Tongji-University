package com.sma.qa.service;

import com.sma.qa.dto.QaAskRequest;
import com.sma.qa.dto.QaAskResponse;
import com.sma.qa.dto.QaHistoryDetailResponse;
import com.sma.qa.dto.QaHistoryListResponse;

public interface QaService {

    QaAskResponse ask(QaAskRequest request);

    QaHistoryListResponse listHistory(String userId, String courseId);

    QaHistoryDetailResponse getHistory(String historyId);
}
