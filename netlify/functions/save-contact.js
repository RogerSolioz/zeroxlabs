// netlify/functions/save-contact.js
exports.handler = async (event, context) => {
  // Vérifier que c'est une requête POST
  if (event.httpMethod !== 'POST') {
    return {
      statusCode: 405,
      body: JSON.stringify({ success: false, error: 'Method not allowed' })
    };
  }

  try {
    const { email, name, message } = JSON.parse(event.body);
    
    // Validation de base
    if (!email || !email.includes('@')) {
      throw new Error('Invalid email address');
    }

    // Préparer les données du contact
    const contactData = {
      timestamp: new Date().toISOString(),
      email: email,
      name: name || 'Not provided',
      message: message || 'No message',
      ip: event.headers['client-ip'] || 'unknown'
    };

    // Sur Netlify, vous pouvez utiliser une base de données externe
    // ou envoyer par email via un service comme EmailJS
    
    // Pour l'instant, on simule le succès
    console.log('Contact received:', contactData);
    
    // Vous pourriez ici :
    // - Envoyer un email via SendGrid/Mailgun
    // - Sauvegarder dans Airtable/Google Sheets
    // - Utiliser Netlify Forms
    
    return {
      statusCode: 200,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        success: true,
        message: 'Contact information saved successfully'
      })
    };

  } catch (error) {
    return {
      statusCode: 500,
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({
        success: false,
        error: error.message
      })
    };
  }
};
