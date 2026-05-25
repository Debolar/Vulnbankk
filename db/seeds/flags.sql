-- VulnBank — seed flag CTF

INSERT INTO flags (id, challenge_id, flag_value, description, difficulty, points)
VALUES
    (1,  'A01', 'PWR{idor_account_takeover}',      'IDOR — dostęp do konta innego użytkownika',    'easy',   100),
    (2,  'A02', 'PWR{debug_config_exposed}',        'Endpoint debug zwraca zmienne środowiskowe',   'easy',   100),
    (3,  'A03', 'PWR{vulnerable_dependency_found}', 'Podatna biblioteka PyYAML 5.3.1 (CVE-2020-14343)', 'easy', 100),
    (4,  'A04', 'PWR{md5_no_salt_cracked}',         'Hasło MD5 bez soli złamane na crackstation',  'medium', 150),
    (5,  'A05', 'PWR{sqli_transactions_leaked}',    'SQL Injection w wyszukiwarce transakcji',      'medium', 150),
    (6,  'A06', 'PWR{insecure_password_reset}',     'Reset hasła przez PESEL bez tokenu email',    'easy',   100),
    (7,  'A07', 'PWR{no_ratelimit_bruteforce}',     'Brute-force logowania bez rate limitingu',    'easy',   100),
    (8,  'A08', 'PWR{jwt_tampered_admin}',          'JWT None Algorithm — bypass autoryzacji admina', 'medium', 150),
    (9,  'A09', 'PWR{logs_exposed_no_auth}',        'Logi z hasłami dostępne bez autoryzacji',     'easy',   100),
    (10, 'A10', 'PWR{stacktrace_db_url_leaked}',    'Stack trace ujawnia connection string z hasłem', 'easy',  100),
    (11,  'A02.1', 'PWR{S0urc3_M4ps_L34k}',        'Aplikacja błędnie udostępnia pliki Source Maps na produkcji',   'easy',   100),
    (12,  'A11', 'PWR{open_r3d1rect_phi1sh1ng_v3ct0r}',        'Phishing przez zaufany URL',   'easy',   100),
    (13, 'A12', 'PWR{ss4f_int3rnal_s3rvice_expos3d}',   'SSRF - dostep do wewnetrznych zasobow', 'medium', 150),
    (14, 'A13', 'PWR{c0mm4nd_1nj3ct10n_rce}', 'Command Injection - zdalne wykonanie kodu', 'hard', 200),
    (16, 'A15', 'PWR{p4th_tr4v3rs4l_s3cr3t_r34d}', 'Path Traversal - odczyt plikow poza katalogiem', 'medium', 150),
    (17, 'A16', 'PWR{p1ckl3_d3s3r14l1z4t10n_rce}', 'Insecure Deserialization - pickle RCE', 'hard', 200),
ON CONFLICT (id) DO NOTHING;

SELECT setval('flags_id_seq', (SELECT MAX(id) FROM flags));
