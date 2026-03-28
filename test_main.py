import io
from fastapi.testclient import TestClient
from PIL import Image
from main import app

client = TestClient(app)

def test_generate_image_success():
    """Test that the endpoint returns a valid PNG image with all fields provided."""
    payload = {
        "header": "TEST HEADER",
        "title": "Test Title",
        "subtitle": "Test Subtitle",
        "footer": "test footer"
    }
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    # Verify it's a valid image
    img = Image.open(io.BytesIO(response.content))
    assert img.size == (512, 512)
    assert img.format == "PNG"

def test_generate_image_minimal_fields():
    """Test that the endpoint works with only a title."""
    payload = {"title": "Only Title"}
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_generate_image_empty_fields():
    """Test that the endpoint works with empty strings."""
    payload = {
        "header": "",
        "title": "",
        "subtitle": "",
        "footer": ""
    }
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_generate_image_missing_fields():
    """Test that the endpoint works when fields are missing from JSON (Pydantic defaults)."""
    payload = {}
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_generate_image_long_text():
    """Test that the endpoint handles very long text (shrinking logic)."""
    payload = {
        "title": "This is a very very long title that should definitely trigger the font shrinking logic to prevent overflow",
        "subtitle": "This is also a very long subtitle that should fit within the canvas width even if it is exceptionally long",
        "header": "LONG HEADER TEXT THAT SHOULD BE SHRUNK",
        "footer": "LONG FOOTER TEXT THAT SHOULD ALSO BE SHRUNK"
    }
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    # Verify it's still a valid image
    img = Image.open(io.BytesIO(response.content))
    assert img.size == (512, 512)

def test_generate_image_with_theme():
    """Test that the endpoint works with a specific theme."""
    payload = {
        "title": "Theme Test",
        "theme": "linkedin-theme-1"
    }
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_generate_image_with_twitter_theme():
    """Test that the endpoint works with the twitter theme."""
    payload = {
        "header": "Anusibi J",
        "title": "Twitter Post Title",
        "subtitle": "This is a subtitle for the twitter post screenshot style theme.",
        "theme": "twitter-theme-1",
        "footer": "@anusibinj"
    }
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    img = Image.open(io.BytesIO(response.content))
    assert img.size == (512, 512)

def test_generate_image_with_ios_theme():
    """Test that the endpoint works with the ios-messages-1 theme."""
    payload = {
        "header": "Receiver Name",
        "title": "Sender message right aligned",
        "subtitle": "Receiver message left aligned",
        "theme": "ios-messages-1"
    }
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    
    img = Image.open(io.BytesIO(response.content))
    assert img.size == (512, 512)

def test_invalid_json():
    """Test that invalid JSON returns a 422 Unprocessable Entity."""
    response = client.post("/generate", content="invalid json")
    assert response.status_code == 422
