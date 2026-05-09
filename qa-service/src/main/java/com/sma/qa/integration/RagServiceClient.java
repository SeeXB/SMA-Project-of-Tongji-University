package com.sma.qa.integration;

import com.sma.qa.dto.RagRetrievalRequest;
import com.sma.qa.dto.RagRetrievalResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

@Component
public class RagServiceClient {

    private final RestTemplate restTemplate;
    private final String ragServiceBaseUrl;

    public RagServiceClient(
            RestTemplate restTemplate,
            @Value("${rag.service.base-url}") String ragServiceBaseUrl
    ) {
        this.restTemplate = restTemplate;
        this.ragServiceBaseUrl = ragServiceBaseUrl;
    }

    public RagRetrievalResponse retrieve(RagRetrievalRequest request) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        return restTemplate.postForObject(
                ragServiceBaseUrl + "/rag/retrieval",
                new HttpEntity<>(request, headers),
                RagRetrievalResponse.class
        );
    }
}
