<?php
header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
    exit;
}

try {
    // Get form data
    $email = filter_var($_POST['email'] ?? '', FILTER_SANITIZE_EMAIL);
    $name = htmlspecialchars($_POST['name'] ?? '', ENT_QUOTES, 'UTF-8');
    $message = htmlspecialchars($_POST['message'] ?? '', ENT_QUOTES, 'UTF-8');
    $timestamp = $_POST['timestamp'] ?? date('c');
    
    // Validate email
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        throw new Exception('Invalid email address');
    }
    
    // Prepare contact data
    $contactData = [
        'timestamp' => $timestamp,
        'email' => $email,
        'name' => $name,
        'message' => $message,
        'ip' => $_SERVER['REMOTE_ADDR'] ?? 'unknown'
    ];
    
    // Format for text file
    $logEntry = sprintf(
        "[%s] Email: %s | Name: %s | IP: %s\nMessage: %s\n%s\n\n",
        $timestamp,
        $email,
        $name ?: 'Not provided',
        $contactData['ip'],
        $message ?: 'No message',
        str_repeat('-', 80)
    );
    
    // Save to contacts.txt file
    $filename = 'contacts.txt';
    $result = file_put_contents($filename, $logEntry, FILE_APPEND | LOCK_EX);
    
    if ($result === false) {
        throw new Exception('Failed to save contact information');
    }
    
    // Also save as JSON for potential future use
    $jsonFilename = 'contacts.json';
    $existingData = [];
    
    if (file_exists($jsonFilename)) {
        $existingJson = file_get_contents($jsonFilename);
        $existingData = json_decode($existingJson, true) ?: [];
    }
    
    $existingData[] = $contactData;
    file_put_contents($jsonFilename, json_encode($existingData, JSON_PRETTY_PRINT), LOCK_EX);
    
    // Return success response
    echo json_encode([
        'success' => true,
        'message' => 'Contact information saved successfully'
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        'success' => false,
        'error' => $e->getMessage()
    ]);
}
?>
