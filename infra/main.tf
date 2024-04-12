resource "aws_cloudwatch_event_connection" "customer_engine_connection" {
  name               = "customer-engine"
  description        = "A connection to send scheduled events to Customer Engine Server"
  authorization_type = "API_KEY"

  auth_parameters {
    api_key {
      key   = "API_KEY"
      value = "1234"
    }
  }
}

resource "aws_cloudwatch_event_api_destination" "test" {
  name                             = "customer-engine-whatsapp-scheduled-events"
  description                      = "An API Destination for customer engine whatsapp scheduled events."
  invocation_endpoint              = "https://webhook.site/ea4bbd44-b896-437c-9143-2abc9389c4a8"
  http_method                      = "POST"
  invocation_rate_limit_per_second = 20
  connection_arn                   = aws_cloudwatch_event_connection.customer_engine_connection.arn
}
