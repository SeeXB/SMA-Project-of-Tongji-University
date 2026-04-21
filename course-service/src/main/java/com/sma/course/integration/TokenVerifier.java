package com.sma.course.integration;

import org.springframework.stereotype.Component;

@Component
public class TokenVerifier {

    public void verify(String accessToken, String userId) {
        if (accessToken == null || accessToken.isBlank() || !accessToken.startsWith("mock-")) {
            throw new IllegalArgumentException("Access token is invalid.");
        }

        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("User id is required.");
        }
    }
}
