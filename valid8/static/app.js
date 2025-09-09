// Certificate Blockchain Manager JavaScript

class CertificateBlockchainManager {
    constructor() {
        this.institutions = {
            "TECH_UNIV_001": {
                name: "Tech University",
                public_key: "pub_key_1",
                status: "active",
                registered_date: "2025-01-01"
            },
            "BIZ_COLLEGE_002": {
                name: "Business College",
                public_key: "pub_key_2",
                status: "active",
                registered_date: "2025-01-02"
            },
            "MED_SCHOOL_003": {
                name: "Medical School",
                public_key: "pub_key_3",
                status: "active",
                registered_date: "2025-01-03"
            }
        };

        this.certificates = [
            {
                certificate_id: "CERT-TECH_UNIV_001-ABC123",
                student_name: "John Doe",
                course_name: "Master of Computer Science",
                institution_id: "TECH_UNIV_001",
                institution_name: "Tech University",
                issue_date: "2025-01-15",
                completion_date: "2024-12-20",
                grade: "A",
                credits: 120,
                certificate_type: "degree",
                hash: "a1b2c3d4e5f6",
                timestamp: "2025-01-15T10:30:00Z"
            },
            {
                certificate_id: "CERT-BIZ_COLLEGE_002-XYZ789",
                student_name: "Jane Smith",
                course_name: "Bachelor of Business Administration",
                institution_id: "BIZ_COLLEGE_002",
                institution_name: "Business College",
                issue_date: "2025-02-01",
                completion_date: "2024-11-30",
                grade: "B+",
                credits: 180,
                certificate_type: "degree",
                hash: "f6e5d4c3b2a1",
                timestamp: "2025-02-01T14:20:00Z"
            },
            {
                certificate_id: "CERT-TECH_UNIV_001-DEF456",
                student_name: "Bob Johnson",
                course_name: "Data Science Certificate",
                institution_id: "TECH_UNIV_001",
                institution_name: "Tech University",
                issue_date: "2025-01-20",
                completion_date: "2025-01-15",
                grade: "A-",
                credits: 30,
                certificate_type: "certificate",
                hash: "1a2b3c4d5e6f",
                timestamp: "2025-01-20T09:15:00Z"
            },
            {
                certificate_id: "CERT-MED_SCHOOL_003-GHI789",
                student_name: "Alice Brown",
                course_name: "Medical Assistant Diploma",
                institution_id: "MED_SCHOOL_003",
                institution_name: "Medical School",
                issue_date: "2025-02-05",
                completion_date: "2024-12-15",
                grade: "B",
                credits: 90,
                certificate_type: "diploma",
                hash: "6f5e4d3c2b1a",
                timestamp: "2025-02-05T16:45:00Z"
            },
            {
                certificate_id: "CERT-BIZ_COLLEGE_002-JKL012",
                student_name: "Charlie Davis",
                course_name: "Project Management Certificate",
                institution_id: "BIZ_COLLEGE_002",
                institution_name: "Business College",
                issue_date: "2025-02-10",
                completion_date: "2025-01-30",
                grade: "A",
                credits: 25,
                certificate_type: "certificate",
                hash: "7g6f5e4d3c2b",
                timestamp: "2025-02-10T11:20:00Z"
            }
        ];

        this.pendingCertificates = [];
        this.blockchain = [
            {
                index: 0,
                timestamp: "2025-01-01T00:00:00Z",
                previous_hash: "0",
                hash: "genesis_hash",
                certificates: [],
                nonce: 0
            },
            {
                index: 1,
                timestamp: "2025-01-15T12:00:00Z",
                previous_hash: "genesis_hash",
                hash: "block_1_hash",
                certificates: ["CERT-TECH_UNIV_001-ABC123", "CERT-BIZ_COLLEGE_002-XYZ789"],
                nonce: 12345
            }
        ];

        this.stats = {
            total_blocks: 2,
            total_certificates: 5,
            pending_certificates: 2,
            authorized_institutions: 3,
            chain_valid: true
        };

        this.init();
    }

    init() {
        this.setupNavigation();
        this.populateInstitutionSelects();
        this.setupEventListeners();
        this.updateDashboard();
        this.showSection('dashboard');
    }

    // Navigation Management
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link[data-section]');
        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.getAttribute('data-section');
                this.showSection(section);
                this.updateActiveNavLink(link);
            });
        });
    }

    showSection(sectionName) {
        const sections = document.querySelectorAll('.section');
        sections.forEach(section => {
            section.classList.remove('active');
        });
        
        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
            targetSection.scrollIntoView({ behavior: 'smooth' });
        }

        // Load section-specific content
        switch(sectionName) {
            case 'dashboard':
                this.updateDashboard();
                break;
            case 'search':
                this.loadSearchResults();
                break;
            case 'blockchain':
                this.updateBlockchainExplorer();
                break;
        }
    }

    updateActiveNavLink(activeLink) {
        const navLinks = document.querySelectorAll('.nav-link[data-section]');
        navLinks.forEach(link => link.classList.remove('active'));
        activeLink.classList.add('active');
    }

    // Institution Management
    populateInstitutionSelects() {
        const selects = [
            'institution-select',
            'bulk-institution-select',
            'search-institution'
        ];

        selects.forEach(selectId => {
            const select = document.getElementById(selectId);
            if (select) {
                // Clear existing options except the first one
                while (select.children.length > 1) {
                    select.removeChild(select.lastChild);
                }

                Object.entries(this.institutions).forEach(([id, institution]) => {
                    const option = document.createElement('option');
                    option.value = id;
                    option.textContent = institution.name;
                    select.appendChild(option);
                });
            }
        });
    }

    // Dashboard Functions
    updateDashboard() {
        // Update stats
        document.getElementById('total-blocks').textContent = this.stats.total_blocks;
        document.getElementById('total-certificates').textContent = this.stats.total_certificates;
        document.getElementById('pending-certificates').textContent = this.stats.pending_certificates;
        document.getElementById('authorized-institutions').textContent = this.stats.authorized_institutions;

        // Update recent certificates
        this.updateRecentCertificates();
        this.updateInstitutionsList();
    }

    updateRecentCertificates() {
        const container = document.getElementById('recent-certificates');
        const recentCerts = this.certificates.slice(-3).reverse();

        container.innerHTML = recentCerts.map(cert => `
            <div class="certificate-card">
                <div class="certificate-header">
                    <div>
                        <h6>${cert.student_name}</h6>
                        <p class="mb-1">${cert.course_name}</p>
                        <small class="text-muted">${cert.institution_name}</small>
                    </div>
                    <div class="certificate-id">${cert.certificate_id}</div>
                </div>
                <div class="certificate-meta">
                    <span><i class="fas fa-calendar me-1"></i> ${this.formatDate(cert.issue_date)}</span>
                    <span><i class="fas fa-medal me-1"></i> ${cert.grade || 'N/A'}</span>
                    <span><i class="fas fa-graduation-cap me-1"></i> ${cert.certificate_type}</span>
                </div>
            </div>
        `).join('');
    }

    updateInstitutionsList() {
        const container = document.getElementById('institutions-list');
        
        container.innerHTML = Object.entries(this.institutions).map(([id, institution]) => `
            <div class="institution-item">
                <div class="institution-icon">
                    <i class="fas fa-university"></i>
                </div>
                <div class="institution-info">
                    <h6>${institution.name}</h6>
                    <small class="status-${institution.status}">${institution.status.toUpperCase()}</small>
                </div>
            </div>
        `).join('');
    }

    // Event Listeners Setup
    setupEventListeners() {
        // Single certificate form
        document.getElementById('single-certificate-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSingleCertificateUpload();
        });

        // CSV upload
        document.getElementById('csv-upload-area').addEventListener('click', () => {
            document.getElementById('csv-file-input').click();
        });

        document.getElementById('csv-file-input').addEventListener('change', (e) => {
            this.handleCSVFileSelection(e.target.files[0]);
        });

        document.getElementById('process-csv-btn').addEventListener('click', () => {
            this.processCSVUpload();
        });

        // Drag and drop
        const uploadArea = document.getElementById('csv-upload-area');
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('drag-over');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('drag-over');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('drag-over');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleCSVFileSelection(files[0]);
            }
        });

        // Search functionality
        document.getElementById('search-btn').addEventListener('click', () => {
            this.performSearch();
        });

        document.getElementById('clear-search-btn').addEventListener('click', () => {
            this.clearSearch();
        });

        // Real-time search
        ['search-student', 'search-course', 'search-institution', 'search-type'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('input', () => {
                    if (this.searchTimeout) clearTimeout(this.searchTimeout);
                    this.searchTimeout = setTimeout(() => this.performSearch(), 300);
                });
            }
        });

        // Verification
        document.getElementById('verify-btn').addEventListener('click', () => {
            this.verifyCertificate();
        });

        // Blockchain operations
        document.getElementById('create-block-btn').addEventListener('click', () => {
            this.createNewBlock();
        });

        document.getElementById('validate-chain-btn').addEventListener('click', () => {
            this.validateBlockchain();
        });
    }

    // Certificate Upload Functions
    handleSingleCertificateUpload() {
        const formData = {
            institution_id: document.getElementById('institution-select').value,
            student_name: document.getElementById('student-name').value,
            course_name: document.getElementById('course-name').value,
            issue_date: document.getElementById('issue-date').value,
            certificate_type: document.getElementById('certificate-type').value,
            grade: document.getElementById('grade').value,
            credits: parseInt(document.getElementById('credits').value) || 0
        };

        if (!formData.institution_id || !formData.student_name || !formData.course_name) {
            this.showError('Please fill in all required fields.');
            return;
        }

        const certificate = this.createCertificate(formData);
        this.certificates.push(certificate);
        this.stats.total_certificates++;
        this.stats.pending_certificates++;

        this.showSuccess(`Certificate created successfully! ID: ${certificate.certificate_id}`);
        document.getElementById('single-certificate-form').reset();
        this.updateDashboard();
    }

    handleCSVFileSelection(file) {
        if (!file || !file.name.endsWith('.csv')) {
            this.showError('Please select a valid CSV file.');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            this.showError('File size must be less than 5MB.');
            return;
        }

        this.selectedCSVFile = file;
        document.getElementById('process-csv-btn').disabled = false;
        
        // Update upload area to show file selected
        const uploadArea = document.getElementById('csv-upload-area');
        uploadArea.innerHTML = `
            <div class="upload-content">
                <i class="fas fa-file-csv upload-icon text-success"></i>
                <h6>${file.name}</h6>
                <p class="text-muted small">File ready for processing</p>
            </div>
        `;
    }

    processCSVUpload() {
        if (!this.selectedCSVFile) {
            this.showError('Please select a CSV file first.');
            return;
        }

        const institutionId = document.getElementById('bulk-institution-select').value;
        if (!institutionId) {
            this.showError('Please select an institution.');
            return;
        }

        const progressContainer = document.getElementById('csv-upload-progress');
        const progressBar = progressContainer.querySelector('.progress-bar');
        
        progressContainer.style.display = 'block';
        progressBar.style.width = '0%';

        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const csv = e.target.result;
                const lines = csv.split('\n').filter(line => line.trim());
                const headers = lines[0].split(',').map(h => h.trim());
                
                let processed = 0;
                const total = lines.length - 1;
                
                // Simulate processing with progress
                const processInterval = setInterval(() => {
                    processed++;
                    const progress = (processed / total) * 100;
                    progressBar.style.width = `${progress}%`;
                    
                    if (processed >= total) {
                        clearInterval(processInterval);
                        setTimeout(() => {
                            this.finishCSVProcessing(lines, headers, institutionId, total);
                            progressContainer.style.display = 'none';
                        }, 500);
                    }
                }, 100);

            } catch (error) {
                this.showError('Error processing CSV file: ' + error.message);
                progressContainer.style.display = 'none';
            }
        };

        reader.readAsText(this.selectedCSVFile);
    }

    finishCSVProcessing(lines, headers, institutionId, total) {
        let successCount = 0;
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            if (values.length >= headers.length) {
                const certData = {
                    institution_id: institutionId,
                    student_name: values[headers.indexOf('student_name')] || '',
                    course_name: values[headers.indexOf('course_name')] || '',
                    issue_date: values[headers.indexOf('issue_date')] || new Date().toISOString().split('T')[0],
                    certificate_type: values[headers.indexOf('certificate_type')] || 'certificate',
                    grade: values[headers.indexOf('grade')] || '',
                    credits: parseInt(values[headers.indexOf('credits')]) || 0,
                    completion_date: values[headers.indexOf('completion_date')] || ''
                };

                if (certData.student_name && certData.course_name) {
                    const certificate = this.createCertificate(certData);
                    this.certificates.push(certificate);
                    successCount++;
                }
            }
        }

        this.stats.total_certificates += successCount;
        this.stats.pending_certificates += successCount;
        
        this.showSuccess(`Successfully processed ${successCount} certificates from CSV.`);
        document.getElementById('process-csv-btn').disabled = true;
        this.updateDashboard();
        
        // Reset upload area
        document.getElementById('csv-upload-area').innerHTML = `
            <div class="upload-content">
                <i class="fas fa-cloud-upload-alt upload-icon"></i>
                <h6>Drop CSV file here or click to browse</h6>
                <p class="text-muted small">Maximum file size: 5MB</p>
            </div>
        `;
    }

    createCertificate(data) {
        const institutionName = this.institutions[data.institution_id]?.name || 'Unknown Institution';
        const certificateId = `CERT-${data.institution_id}-${this.generateId()}`;
        const hash = this.generateHash(certificateId + data.student_name + data.course_name);
        
        return {
            certificate_id: certificateId,
            student_name: data.student_name,
            course_name: data.course_name,
            institution_id: data.institution_id,
            institution_name: institutionName,
            issue_date: data.issue_date,
            completion_date: data.completion_date || data.issue_date,
            grade: data.grade,
            credits: data.credits,
            certificate_type: data.certificate_type,
            hash: hash,
            timestamp: new Date().toISOString()
        };
    }

    // Search Functions
    loadSearchResults() {
        this.performSearch();
    }

    performSearch() {
        const filters = {
            student: document.getElementById('search-student').value.toLowerCase(),
            course: document.getElementById('search-course').value.toLowerCase(),
            institution: document.getElementById('search-institution').value,
            type: document.getElementById('search-type').value
        };

        let results = this.certificates.filter(cert => {
            return (!filters.student || cert.student_name.toLowerCase().includes(filters.student)) &&
                   (!filters.course || cert.course_name.toLowerCase().includes(filters.course)) &&
                   (!filters.institution || cert.institution_id === filters.institution) &&
                   (!filters.type || cert.certificate_type === filters.type);
        });

        this.displaySearchResults(results);
    }

    displaySearchResults(results) {
        const container = document.getElementById('search-results');
        
        if (results.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <h5>No certificates found</h5>
                    <p class="text-muted">Try adjusting your search criteria</p>
                </div>
            `;
            return;
        }

        const resultsHtml = `
            <div class="search-result-count">
                Found ${results.length} certificate${results.length !== 1 ? 's' : ''}
            </div>
            <div class="row g-3">
                ${results.map(cert => `
                    <div class="col-lg-6">
                        <div class="certificate-card">
                            <div class="certificate-header">
                                <div>
                                    <h6>${cert.student_name}</h6>
                                    <p class="mb-1">${cert.course_name}</p>
                                    <small class="text-muted">${cert.institution_name}</small>
                                </div>
                                <div class="certificate-id">${cert.certificate_id}</div>
                            </div>
                            <div class="certificate-meta">
                                <span><i class="fas fa-calendar me-1"></i> ${this.formatDate(cert.issue_date)}</span>
                                <span><i class="fas fa-medal me-1"></i> ${cert.grade || 'N/A'}</span>
                                <span><i class="fas fa-graduation-cap me-1"></i> ${cert.certificate_type}</span>
                                ${cert.credits ? `<span><i class="fas fa-star me-1"></i> ${cert.credits} credits</span>` : ''}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        container.innerHTML = resultsHtml;
    }

    clearSearch() {
        ['search-student', 'search-course', 'search-institution', 'search-type'].forEach(id => {
            document.getElementById(id).value = '';
        });
        this.performSearch();
    }

    // Verification Functions
    verifyCertificate() {
        const certificateId = document.getElementById('verify-certificate-id').value.trim();
        
        if (!certificateId) {
            this.showError('Please enter a certificate ID.');
            return;
        }

        const certificate = this.certificates.find(cert => cert.certificate_id === certificateId);
        const container = document.getElementById('verification-result');

        if (certificate) {
            // Simulate hash verification
            const isValid = this.verifyHash(certificate);
            
            container.innerHTML = `
                <div class="verification-result valid fade-in-up">
                    <div class="verification-icon valid">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <h4>Certificate Verified</h4>
                    <p class="mb-4">This certificate is valid and has been verified on the blockchain.</p>
                    
                    <div class="card">
                        <div class="card-body">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <strong>Student:</strong><br>
                                    ${certificate.student_name}
                                </div>
                                <div class="col-md-6">
                                    <strong>Course:</strong><br>
                                    ${certificate.course_name}
                                </div>
                                <div class="col-md-6">
                                    <strong>Institution:</strong><br>
                                    ${certificate.institution_name}
                                </div>
                                <div class="col-md-6">
                                    <strong>Issue Date:</strong><br>
                                    ${this.formatDate(certificate.issue_date)}
                                </div>
                                <div class="col-md-6">
                                    <strong>Grade:</strong><br>
                                    ${certificate.grade || 'N/A'}
                                </div>
                                <div class="col-md-6">
                                    <strong>Credits:</strong><br>
                                    ${certificate.credits || 'N/A'}
                                </div>
                                <div class="col-12">
                                    <strong>Certificate Hash:</strong><br>
                                    <code>${certificate.hash}</code>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="verification-result invalid fade-in-up">
                    <div class="verification-icon invalid">
                        <i class="fas fa-times-circle"></i>
                    </div>
                    <h4>Certificate Not Found</h4>
                    <p>The certificate ID "${certificateId}" was not found in the blockchain.</p>
                    <p class="text-muted">Please check the certificate ID and try again.</p>
                </div>
            `;
        }
    }

    verifyHash(certificate) {
        // Simulate hash verification - in reality this would check against blockchain
        return certificate.hash && certificate.hash.length > 0;
    }

    // Blockchain Functions
    createNewBlock() {
        if (this.stats.pending_certificates === 0) {
            this.showError('No pending certificates to include in the block.');
            return;
        }

        const pendingCerts = this.certificates.filter(cert => 
            !this.blockchain.some(block => block.certificates.includes(cert.certificate_id))
        );

        if (pendingCerts.length === 0) {
            this.showError('No pending certificates found.');
            return;
        }

        const previousBlock = this.blockchain[this.blockchain.length - 1];
        const newBlock = {
            index: this.blockchain.length,
            timestamp: new Date().toISOString(),
            previous_hash: previousBlock.hash,
            hash: this.generateHash(`block_${this.blockchain.length}_${Date.now()}`),
            certificates: pendingCerts.slice(0, Math.min(5, pendingCerts.length)).map(cert => cert.certificate_id),
            nonce: Math.floor(Math.random() * 100000)
        };

        this.blockchain.push(newBlock);
        this.stats.total_blocks++;
        this.stats.pending_certificates = Math.max(0, this.stats.pending_certificates - newBlock.certificates.length);

        this.showSuccess(`Block #${newBlock.index} created successfully with ${newBlock.certificates.length} certificates.`);
        this.updateDashboard();
        this.updateBlockchainExplorer();
    }

    validateBlockchain() {
        let isValid = true;
        let errorMsg = '';

        for (let i = 1; i < this.blockchain.length; i++) {
            const currentBlock = this.blockchain[i];
            const previousBlock = this.blockchain[i - 1];

            if (currentBlock.previous_hash !== previousBlock.hash) {
                isValid = false;
                errorMsg = `Block ${i} has invalid previous hash`;
                break;
            }

            if (!currentBlock.hash || currentBlock.hash.length === 0) {
                isValid = false;
                errorMsg = `Block ${i} has invalid hash`;
                break;
            }
        }

        this.stats.chain_valid = isValid;
        const statusBadge = document.getElementById('chain-status');

        if (isValid) {
            statusBadge.textContent = 'Valid Chain';
            statusBadge.className = 'badge bg-success';
            this.showSuccess('Blockchain validation successful! All blocks are valid.');
        } else {
            statusBadge.textContent = 'Invalid Chain';
            statusBadge.className = 'badge bg-danger';
            this.showError('Blockchain validation failed: ' + errorMsg);
        }
    }

    updateBlockchainExplorer() {
        const container = document.getElementById('blockchain-explorer');
        
        const blocksHtml = this.blockchain.slice().reverse().map(block => `
            <div class="block-item fade-in-up">
                <div class="block-header">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <div class="block-number">Block #${block.index}</div>
                            <small class="text-muted">${this.formatDateTime(block.timestamp)}</small>
                        </div>
                        <div class="text-end">
                            <small class="text-muted">Nonce: ${block.nonce}</small>
                        </div>
                    </div>
                    <div class="block-hash mt-2">
                        <strong>Hash:</strong> ${block.hash}
                    </div>
                    ${block.previous_hash !== "0" ? `
                        <div class="block-hash">
                            <strong>Previous:</strong> ${block.previous_hash}
                        </div>
                    ` : ''}
                </div>
                <div class="block-body">
                    <h6>Certificates (${block.certificates.length})</h6>
                    ${block.certificates.length > 0 ? `
                        <div class="block-certificates">
                            ${block.certificates.map(certId => {
                                const cert = this.certificates.find(c => c.certificate_id === certId);
                                return cert ? `
                                    <div class="block-certificate">
                                        <strong>${cert.student_name}</strong> - ${cert.course_name}
                                        <br><small>${certId}</small>
                                    </div>
                                ` : `<div class="block-certificate">${certId}</div>`;
                            }).join('')}
                        </div>
                    ` : '<p class="text-muted">No certificates in this block</p>'}
                </div>
            </div>
        `).join('');

        container.innerHTML = blocksHtml || '<p class="text-center text-muted">No blocks found</p>';
    }

    // Utility Functions
    generateId() {
        return Math.random().toString(36).substring(2, 8).toUpperCase();
    }

    generateHash(input) {
        // Simple hash simulation - in reality would use SHA-256
        let hash = 0;
        for (let i = 0; i < input.length; i++) {
            const char = input.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32bit integer
        }
        return Math.abs(hash).toString(16);
    }

    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    formatDateTime(dateString) {
        return new Date(dateString).toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    showSuccess(message) {
        document.getElementById('success-message').textContent = message;
        new bootstrap.Modal(document.getElementById('successModal')).show();
    }

    showError(message) {
        document.getElementById('error-message').textContent = message;
        new bootstrap.Modal(document.getElementById('errorModal')).show();
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.certificateManager = new CertificateBlockchainManager();
});