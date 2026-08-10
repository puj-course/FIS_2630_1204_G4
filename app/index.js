const express = require("express");

const app = express();

const PORT = 3000;

app.get("/", (req, res) => {
    res.send(`
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Aplicación Docker</title>
            <style>
                body {
                    margin: 0;
                    font-family: Arial, Helvetica, sans-serif;
                    background: linear-gradient(135deg, #dbeafe, #eff6ff, #ffffff);
                    color: #1f2937;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }

                .card {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 48px 42px;
                    border-radius: 24px;
                    box-shadow: 0 18px 45px rgba(15, 23, 42, 0.16);
                    max-width: 680px;
                    text-align: center;
                    border: 1px solid #e2e8f0;
                }

                .badge {
                    display: inline-block;
                    background: #dbeafe;
                    color: #1d4ed8;
                    padding: 9px 18px;
                    border-radius: 999px;
                    font-size: 14px;
                    font-weight: bold;
                    letter-spacing: 0.4px;
                    margin-bottom: 24px;
                }

                h1 {
                    font-size: 38px;
                    margin: 0 0 28px 0;
                    color: #0f172a;
                    line-height: 1.2;
                }

                .info {
                    background: linear-gradient(135deg, #eff6ff, #dbeafe);
                    border: 1px solid #bfdbfe;
                    padding: 22px;
                    border-radius: 16px;
                    text-align: center;
                    margin-top: 10px;
                }

                .course {
                    color: #1e3a8a;
                    font-size: 22px;
                    font-weight: 800;
                    margin-bottom: 6px;
                }

                .university {
                    color: #1d4ed8;
                    font-size: 18px;
                    font-weight: 600;
                }

                .footer {
                    margin-top: 28px;
                    font-size: 14px;
                    color: #64748b;
                }
            </style>
        </head>
        <body>
            <div class="card">
                <div class="badge">Docker + Node.js</div>

                <h1>Aplicación funcionando correctamente</h1>

                <div class="info">
                    <div class="course">Fundamentos de Ingeniería de Software</div>
                    <div class="university">PUJ</div>
                </div>

                <div class="footer">
                    Ejercicio práctico de contenerización con Docker
                </div>
            </div>
        </body>
        </html>
    `);
});

app.listen(PORT, () => {
    console.log(`Servidor ejecutándose en puerto ${PORT}`);
});