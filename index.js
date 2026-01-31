const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const bodyParser = require('body-parser');
const multer = require('multer');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Set up multer for file uploads
const upload = multer({ dest: 'uploads/' });

// Initialize SQLite database
const dbPath = path.join(__dirname, 'admission.db');
const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
  } else {
    console.log('Connected to SQLite database');
  }
});

// Create tables
db.serialize(() => {
  // Create applicants table
  db.run(`CREATE TABLE IF NOT EXISTS applicants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    total_score REAL,
    priority INTEGER,
    date_submitted TEXT,
    UNIQUE(name, program)
  )`);

  // Create programs table
  db.run(`CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    budget_places INTEGER DEFAULT 0
  )`);

  // Insert initial programs with their budget places
  const programs = [
    { name: 'Прикладная математика (ПМ)', places: 40 },
    { name: 'Информатика и вычислительная техника (ИВТ)', places: 50 },
    { name: 'Инфокоммуникационные технологии и системы связи (ИТСС)', places: 30 }
  ];

  programs.forEach(program => {
    db.run(
      `INSERT OR IGNORE INTO programs (name, budget_places) VALUES (?, ?)`,
      [program.name, program.places]
    );
  });
});

// API Routes

// Get all programs
app.get('/api/programs', (req, res) => {
  db.all('SELECT * FROM programs ORDER BY name', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// Get applicants for a specific program
app.get('/api/applicants/:program', (req, res) => {
  const program = req.params.program;
  db.all(
    `SELECT * FROM applicants WHERE program = ? ORDER BY total_score DESC, priority ASC`,
    [program],
    (err, rows) => {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      res.json(rows);
    }
  );
});

// Get all applicants
app.get('/api/applicants', (req, res) => {
  db.all('SELECT * FROM applicants ORDER BY program, total_score DESC, priority ASC', [], (err, rows) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    res.json(rows);
  });
});

// Import csv-parse library
const fs = require('fs');
const { parse } = require('csv-parse');

// Upload and process CSV file
app.post('/api/upload', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const filePath = req.file.path;
  const results = [];
  
  // Extract date from filename if possible (e.g., pm_01.csv -> 01.08.2023)
  let dateFromFilename = null;
  const filenameMatch = req.file.originalname.match(/_(\d{2})\.csv$/);
  if (filenameMatch) {
    // Assuming August 2023 for demonstration purposes
    dateFromFilename = `2023-08-${filenameMatch[1]}`;
  } else {
    // Extract date from format like pm_01_08.csv
    const extendedMatch = req.file.originalname.match(/_(\d{2})_(\d{2})\.csv$/);
    if (extendedMatch) {
      dateFromFilename = `2023-${extendedMatch[2]}-${extendedMatch[1]}`;
    }
  }
  
  // Extract program from filename
  let programFromFilename = null;
  const programMatch = req.file.originalname.match(/^(pm|ivt|itss)_/);
  if (programMatch) {
    switch(programMatch[1]) {
      case 'pm':
        programFromFilename = 'Прикладная математика (ПМ)';
        break;
      case 'ivt':
        programFromFilename = 'Информатика и вычислительная техника (ИВТ)';
        break;
      case 'itss':
        programFromFilename = 'Инфокоммуникационные технологии и системы связи (ИТСС)';
        break;
    }
  }

  // Parse CSV file
  fs.createReadStream(filePath)
    .pipe(parse({ columns: true, skip_empty_lines: true }))
    .on('data', (data) => {
      // Convert fields to proper types
      results.push({
        name: data.name,
        total_score: parseFloat(data.total_score),
        priority: parseInt(data.priority),
        program: req.body.program || programFromFilename || 'Unknown Program',
        date_submitted: dateFromFilename || new Date().toISOString().split('T')[0]
      });
    })
    .on('end', () => {
      // Clean up uploaded file
      fs.unlinkSync(filePath);

      // Update database with parsed data
      db.serialize(() => {
        db.run('BEGIN TRANSACTION');

        results.forEach((applicant) => {
          const { name, total_score, priority, program, date_submitted } = applicant;
          
          // Check if applicant already exists
          const checkSql = `SELECT id FROM applicants WHERE name = ? AND program = ?`;
          db.get(checkSql, [name, program], (err, row) => {
            if (err) {
              console.error('Error checking applicant:', err);
              return;
            }

            if (row) {
              // Update existing applicant
              const updateSql = `
                UPDATE applicants 
                SET total_score = ?, priority = ?, date_submitted = ?
                WHERE name = ? AND program = ?
              `;
              db.run(updateSql, [total_score, priority, date_submitted, name, program], (err) => {
                if (err) {
                  console.error('Error updating applicant:', err);
                }
              });
            } else {
              // Insert new applicant
              const insertSql = `
                INSERT INTO applicants (name, program, total_score, priority, date_submitted)
                VALUES (?, ?, ?, ?, ?)
              `;
              db.run(insertSql, [name, program, total_score, priority, date_submitted], (err) => {
                if (err) {
                  console.error('Error inserting applicant:', err);
                }
              });
            }
          });
        });

        // Commit transaction
        db.run('COMMIT', (err) => {
          if (err) {
            console.error('Error committing transaction:', err);
            res.status(500).json({ error: err.message });
          } else {
            res.json({ 
              message: `Successfully processed ${results.length} applicants from CSV`, 
              count: results.length 
            });
          }
        });
      });
    })
    .on('error', (error) => {
      console.error('Error parsing CSV:', error);
      fs.unlinkSync(filePath); // Clean up file even if there's an error
      res.status(500).json({ error: error.message });
    });
});

// Update database with new applicant data
app.post('/api/update-applicants', (req, res) => {
  const { applicants } = req.body;
  
  if (!Array.isArray(applicants)) {
    return res.status(400).json({ error: 'Applicants must be an array' });
  }

  let processedCount = 0;
  let errorCount = 0;

  db.serialize(() => {
    // Begin transaction for performance
    db.run('BEGIN TRANSACTION');

    applicants.forEach((applicant) => {
      const { name, program, total_score, priority, date_submitted } = applicant;
      
      // Check if applicant already exists
      const checkSql = `SELECT id FROM applicants WHERE name = ? AND program = ?`;
      db.get(checkSql, [name, program], (err, row) => {
        if (err) {
          console.error('Error checking applicant:', err);
          errorCount++;
          return;
        }

        if (row) {
          // Update existing applicant
          const updateSql = `
            UPDATE applicants 
            SET total_score = ?, priority = ?, date_submitted = ?
            WHERE name = ? AND program = ?
          `;
          db.run(updateSql, [total_score, priority, date_submitted, name, program], (err) => {
            if (err) {
              console.error('Error updating applicant:', err);
              errorCount++;
            } else {
              processedCount++;
            }
          });
        } else {
          // Insert new applicant
          const insertSql = `
            INSERT INTO applicants (name, program, total_score, priority, date_submitted)
            VALUES (?, ?, ?, ?, ?)
          `;
          db.run(insertSql, [name, program, total_score, priority, date_submitted], (err) => {
            if (err) {
              console.error('Error inserting applicant:', err);
              errorCount++;
            } else {
              processedCount++;
            }
          });
        }
      });
    });

    // Commit transaction after a short delay to ensure all operations complete
    setTimeout(() => {
      db.run('COMMIT', (err) => {
        if (err) {
          console.error('Error committing transaction:', err);
          res.status(500).json({ error: err.message });
        } else {
          res.json({ 
            message: `Processed ${processedCount} applicants`, 
            errors: errorCount 
          });
        }
      });
    }, 1000);
  });
});

// Delete applicants not present in new data
app.post('/api/cleanup-applicants', (req, res) => {
  const { currentApplicants } = req.body;
  
  if (!Array.isArray(currentApplicants)) {
    return res.status(400).json({ error: 'Current applicants must be an array' });
  }

  // Create a temporary table to hold current applicants
  db.serialize(() => {
    db.run('BEGIN TRANSACTION');
    
    // Create temporary table
    db.run('CREATE TEMP TABLE temp_current_applicants (name TEXT, program TEXT)');
    
    // Insert current applicants into temp table
    const stmt = db.prepare('INSERT INTO temp_current_applicants VALUES (?, ?)');
    currentApplicants.forEach(applicant => {
      stmt.run([applicant.name, applicant.program]);
    });
    stmt.finalize();
    
    // Delete applicants not in the current list
    db.run(`
      DELETE FROM applicants 
      WHERE id IN (
        SELECT a.id 
        FROM applicants a 
        LEFT JOIN temp_current_applicants t ON a.name = t.name AND a.program = t.program 
        WHERE t.name IS NULL
      )
    `, (err) => {
      if (err) {
        console.error('Error during cleanup:', err);
        db.run('ROLLBACK');
        res.status(500).json({ error: err.message });
      } else {
        db.run('COMMIT', () => {
          res.json({ message: 'Cleanup completed successfully' });
        });
      }
    });
  });
});

// Calculate admission probabilities
app.get('/api/admission-probabilities/:program', (req, res) => {
  const program = req.params.program;
  
  // Get program info
  db.get('SELECT budget_places FROM programs WHERE name = ?', [program], (err, programInfo) => {
    if (err) {
      res.status(500).json({ error: err.message });
      return;
    }
    
    if (!programInfo) {
      res.status(404).json({ error: 'Program not found' });
      return;
    }
    
    // Get all applicants for this program ordered by score
    db.all(
      `SELECT * FROM applicants WHERE program = ? ORDER BY total_score DESC, priority ASC`,
      [program],
      (err, allApplicants) => {
        if (err) {
          res.status(500).json({ error: err.message });
          return;
        }
        
        const budgetPlaces = programInfo.budget_places;
        const rankedApplicants = allApplicants.map((applicant, index) => {
          let status = 'Не поступил';
          
          if (index < budgetPlaces) {
            status = 'Поступил';
          } else if (index < budgetPlaces + 5) { // Within next 5 positions
            status = 'На грани';
          }
          
          return {
            ...applicant,
            rank: index + 1,
            probability: index < budgetPlaces ? 100 : Math.max(0, 100 - ((index - budgetPlaces + 1) * 10)),
            status
          };
        });
        
        res.json(rankedApplicants);
      }
    );
  });
});

// Get historical data for a program
app.get('/api/historical-data/:program', (req, res) => {
  const program = req.params.program;
  
  db.all(
    `SELECT * FROM applicants WHERE program = ? ORDER BY date_submitted, total_score DESC`,
    [program],
    (err, rows) => {
      if (err) {
        res.status(500).json({ error: err.message });
        return;
      }
      
      // Group by date to show dynamics
      const groupedByDate = {};
      rows.forEach(row => {
        if (!groupedByDate[row.date_submitted]) {
          groupedByDate[row.date_submitted] = [];
        }
        groupedByDate[row.date_submitted].push(row);
      });
      
      // Sort dates chronologically
      const sortedDates = Object.keys(groupedByDate).sort();
      const result = sortedDates.map(date => ({
        date: date,
        applicants: groupedByDate[date]
      }));
      
      res.json(result);
    }
  );
});

// Serve the main HTML page
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});