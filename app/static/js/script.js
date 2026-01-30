// JavaScript for the Admission Analysis System

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const dateSelector = document.getElementById('date-selector');
    const loadDataBtn = document.getElementById('load-data-btn');
    const calculatePassingScoresBtn = document.getElementById('calculate-passing-scores-btn');
    const generateReportBtn = document.getElementById('generate-report-btn');
    const programFilter = document.getElementById('program-filter');
    const priorityFilter = document.getElementById('priority-filter');
    const consentFilter = document.getElementById('consent-filter');
    
    // Load initial data
    loadApplicantsData();
    loadStatsData();
    
    // Event listeners
    loadDataBtn.addEventListener('click', loadApplicantsData);
    calculatePassingScoresBtn.addEventListener('click', calculatePassingScores);
    generateReportBtn.addEventListener('click', generateReport);
    
    // Filter event listeners
    programFilter.addEventListener('change', loadApplicantsData);
    priorityFilter.addEventListener('change', loadApplicantsData);
    consentFilter.addEventListener('change', loadApplicantsData);
    
    // Function to load applicants data
    async function loadApplicantsData() {
        try {
            const selectedDate = dateSelector.value;
            const program = programFilter.value;
            const priority = priorityFilter.value;
            const consent = consentFilter.checked;
            
            // Simulate API call to get applicants data
            const response = await fetch(`/api/applicants?date=${selectedDate}&program=${program}&priority=${priority}&consent=${consent}`);
            const data = await response.json();
            
            populateApplicantsTable(data.applicants || []);
        } catch (error) {
            console.error('Error loading applicants data:', error);
        }
    }
    
    // Function to load statistics data
    async function loadStatsData() {
        try {
            const selectedDate = dateSelector.value;
            
            // Simulate API call to get stats data
            const response = await fetch(`/api/stats?date=${selectedDate}`);
            const data = await response.json();
            
            populateStatsTable(data.stats || []);
        } catch (error) {
            console.error('Error loading stats data:', error);
        }
    }
    
    // Function to calculate passing scores
    async function calculatePassingScores() {
        try {
            const selectedDate = dateSelector.value;
            
            const response = await fetch(`/passing_scores?date=${selectedDate}`);
            const data = await response.json();
            
            alert(`Проходные баллы рассчитаны для ${selectedDate}.\nОткройте консоль для деталей.`);
            console.log('Passing scores:', data);
            
            // Reload stats to show updated passing scores
            loadStatsData();
        } catch (error) {
            console.error('Error calculating passing scores:', error);
        }
    }
    
    // Function to generate report
    async function generateReport() {
        try {
            const selectedDate = dateSelector.value;
            
            const response = await fetch('/generate_report', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ date: selectedDate })
            });
            
            if (response.ok) {
                // Create a download link for the PDF
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `report_${selectedDate}.pdf`;
                document.body.appendChild(a);
                a.click();
                a.remove();
                window.URL.revokeObjectURL(url);
            } else {
                console.error('Error generating report:', response.statusText);
            }
        } catch (error) {
            console.error('Error generating report:', error);
        }
    }
    
    // Function to populate applicants table
    function populateApplicantsTable(applicants) {
        const tbody = document.getElementById('applicants-body');
        tbody.innerHTML = '';
        
        applicants.forEach(applicant => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${applicant.applicant_id || ''}</td>
                <td>${applicant.educational_program || ''}</td>
                <td>${applicant.priority_op || ''}</td>
                <td>${applicant.consent_given ? 'Да' : 'Нет'}</td>
                <td>${applicant.physics_ikt || 0}</td>
                <td>${applicant.russian_lang || 0}</td>
                <td>${applicant.math || 0}</td>
                <td>${applicant.individual_achievements || 0}</td>
                <td>${applicant.total_score || 0}</td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    // Function to populate stats table
    function populateStatsTable(stats) {
        const tbody = document.getElementById('stats-body');
        tbody.innerHTML = '';
        
        stats.forEach(stat => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${stat.program_name || ''}</td>
                <td>${stat.code || ''}</td>
                <td>${stat.places || 0}</td>
                <td>${stat.applications || 0}</td>
                <td>${stat.with_consent || 0}</td>
                <td>${stat.passing_score || 'Н/Д'}</td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    // Initialize chart if element exists
    const chartCanvas = document.getElementById('passingScoresChart');
    if (chartCanvas) {
        const ctx = chartCanvas.getContext('2d');
        // Create a simple placeholder chart
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['1 авг', '2 авг', '3 авг', '4 авг'],
                datasets: [{
                    label: 'Прикладная математика (ПМ)',
                    data: [250, 280, 320, 340],
                    borderColor: 'rgb(255, 99, 132)',
                    tension: 0.1
                }, {
                    label: 'Информатика и вычислительная техника (ИВТ)',
                    data: [230, 260, 290, 310],
                    borderColor: 'rgb(54, 162, 235)',
                    tension: 0.1
                }, {
                    label: 'Инфокоммуникационные технологии и системы связи (ИТСС)',
                    data: [200, 220, 240, 260],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }, {
                    label: 'Информационная безопасность (ИБ)',
                    data: [220, 250, 270, 290],
                    borderColor: 'rgb(153, 102, 255)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Динамика проходных баллов по программам'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false
                    }
                }
            }
        });
    }
});