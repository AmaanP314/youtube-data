async function fetchVisualizations() {
    try {
      const response = await fetch('/fetch_visualizations');
      const data = await response.json();
      
      if (!data.error && data) {
        const totalPlaceholder = document.getElementById("total-placeholder");
        const engagementPlaceholder = document.getElementById("engagement-rate-placeholder");
        const compositePlaceholder = document.getElementById("composite-score-placeholder");
        if (totalPlaceholder && data.total_plot) {
          totalPlaceholder.src = `data:image/png;base64,${data.total_plot}`;
          totalPlaceholder.style.opacity = 1;
        }
  
        if (engagementPlaceholder && data.engagement_rate_plot) {
          engagementPlaceholder.src = `data:image/png;base64,${data.engagement_rate_plot}`;
          engagementPlaceholder.style.opacity = 1;
        }
  
        if (compositePlaceholder && data.composite_score_plot) {
          compositePlaceholder.src = `data:image/png;base64,${data.composite_score_plot}`;
          compositePlaceholder.style.opacity = 1;
        }
      } else {
        console.error("Error in visualization response:", data.error || "No data available");
      }
      const response_senti = await fetch('/sentiment_analysis');
      const data_senti = await response_senti.json();

      if (!data_senti.error && data_senti) {
        const sentimentPlaceholder = document.getElementById("sentiment-placeholder");
        if (sentimentPlaceholder && data_senti.senti_plot) {
          sentimentPlaceholder.src = `data:image/png;base64,${data_senti.senti_plot}`;
          sentimentPlaceholder.style.opacity = 1;
        }
      } else {
        console.error("Error in sentiment analysis response:", data_senti.error || "No sentiment data available");
      }
    } catch (error) {
      console.error("Error fetching visualizations:", error);
  
      // Show an error alert on the page
      const container = document.querySelector('.container');
      const alertDiv = document.createElement('div');
      alertDiv.className = 'alert alert-danger mt-3';
      alertDiv.role = 'alert';
      alertDiv.textContent = `An error occurred while loading visualizations: ${error.message}`;
      container.appendChild(alertDiv);
    }
  }
  window.onload = fetchVisualizations;