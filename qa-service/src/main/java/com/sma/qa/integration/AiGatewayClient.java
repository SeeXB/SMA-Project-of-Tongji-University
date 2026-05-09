package com.sma.qa.integration;

import com.sma.qa.dto.AiInferenceRequest;
import com.sma.qa.dto.AiInferenceResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class AiGatewayClient {

    private final RestTemplate restTemplate;
    private final String aiGatewayBaseUrl;

    public AiGatewayClient(
            RestTemplate restTemplate,
            @Value("${ai.gateway.base-url}") String aiGatewayBaseUrl
    ) {
        this.restTemplate = restTemplate;
        this.aiGatewayBaseUrl = aiGatewayBaseUrl;
    }

    public AiInferenceResponse inferSync(AiInferenceRequest request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        return restTemplate.postForObject(
                aiGatewayBaseUrl + "/ai/infer-sync",
                new HttpEntity<>(request, headers),
                AiInferenceResponse.class
        );
    }
}
