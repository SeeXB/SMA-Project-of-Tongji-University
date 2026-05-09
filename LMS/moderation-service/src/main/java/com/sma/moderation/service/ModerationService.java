package com.sma.moderation.service;

import com.sma.moderation.dto.ModerationFileRequest;
import com.sma.moderation.dto.ModerationFileResponse;
import com.sma.moderation.dto.ModerationTextRequest;
import com.sma.moderation.dto.ModerationTextResponse;

public interface ModerationService {

    ModerationTextResponse moderateText(ModerationTextRequest request);

    ModerationFileResponse moderateFile(ModerationFileRequest request);
}
