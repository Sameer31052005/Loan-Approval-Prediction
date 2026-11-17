/**
 * AURA CREDENCE AI - Frontend Orchestration Engine
 * Handles dual-slider sync, segmented tenure pills, master credit cards,
 * SVG radial gauge physics, Decision Tree pathfinder, and report modal.
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- Form & Financial Inputs ---
  const form = document.getElementById('loanForm');
  const applicantIncomeInput = document.getElementById('applicantIncome');
  const applicantIncomeSlider = document.getElementById('applicantIncomeSlider');
  const applicantIncomeBadge = document.getElementById('applicantIncomeBadge');

  const coapplicantIncomeInput = document.getElementById('coapplicantIncome');
  const coapplicantIncomeSlider = document.getElementById('coapplicantIncomeSlider');
  const coapplicantIncomeBadge = document.getElementById('coapplicantIncomeBadge');

  const combinedIncomeDisplay = document.getElementById('combinedIncomeDisplay');
  const annualizedIncomeDisplay = document.getElementById('annualizedIncomeDisplay');

  const loanAmountInput = document.getElementById('loanAmount');
  const loanAmountSlider = document.getElementById('loanAmountSlider');
  const loanAmountBadge = document.getElementById('loanAmountBadge');

  const loanTermInput = document.getElementById('loanTermInput');
  const termBadge = document.getElementById('termBadge');
  const termPills = document.querySelectorAll('.term-pill');
  const liveEmiQuickCalc = document.getElementById('liveEmiQuickCalc');

  const resetBtn = document.getElementById('resetBtn');
  const submitBtn = document.getElementById('submitAssessmentBtn');
  const spinner = document.getElementById('spinner');

  // --- Credit History Master Cards ---
  const chCleanCard = document.getElementById('chCleanCard');
  const chBadCard = document.getElementById('chBadCard');
  const creditStatusBadge = document.getElementById('creditStatusBadge');
  const chRadios = document.querySelectorAll('input[name="Credit_History"]');

  // --- Results HUD Elements ---
  const verdictHologram = document.getElementById('verdictHologram');
  const verdictMainTitle = document.getElementById('verdictMainTitle');
  const verdictIconBox = document.getElementById('verdictIconBox');
  const riskBadge = document.getElementById('riskBadge');
  const ruleLeafTag = document.getElementById('ruleLeafTag');

  const radialProgress = document.getElementById('radialProgress');
  const gaugePctText = document.getElementById('gaugePctText');
  const approvalPctNumber = document.getElementById('approvalPctNumber');
  const rejectionPctNumber = document.getElementById('rejectionPctNumber');
  const approvalFillBar = document.getElementById('approvalFillBar');
  const rejectionFillBar = document.getElementById('rejectionFillBar');

  const hudTotalIncome = document.getElementById('hudTotalIncome');
  const hudLoanAmount = document.getElementById('hudLoanAmount');
  const hudMonthlyEmi = document.getElementById('hudMonthlyEmi');
  const hudDti = document.getElementById('hudDti');
  const treePathSteps = document.getElementById('treePathSteps');
  const directiveText = document.getElementById('directiveText');

  // --- Navigation & Modal Elements ---
  const toggleMetricsTabBtn = document.getElementById('toggleMetricsTabBtn');
  const diagnosticsSection = document.getElementById('diagnosticsSection');
  const openReportModalBtn = document.getElementById('openReportModalBtn');
  const reportModalBackdrop = document.getElementById('reportModalBackdrop');
  const btnCloseDrawer = document.getElementById('btnCloseDrawer');
  const btnCopyReport = document.getElementById('btnCopyReport');
  const toastMessage = document.getElementById('toastMessage');

  // SVG Gauge Math: 2 * PI * 64 = 402.12
  const GAUGE_CIRCUMFERENCE = 2 * Math.PI * 64;
  radialProgress.style.strokeDasharray = `${GAUGE_CIRCUMFERENCE}`;

  // =========================================================================
  // Dual-Slider & Numeric Synchronization
  // =========================================================================
  function syncIncome() {
    const val = parseFloat(applicantIncomeInput.value) || 0;
    applicantIncomeSlider.value = Math.min(val, 40000);
    applicantIncomeBadge.textContent = `₹${val.toLocaleString('en-IN')} / mo`;
    recalcAggregates();
  }

  function syncIncomeFromSlider() {
    applicantIncomeInput.value = applicantIncomeSlider.value;
    syncIncome();
  }

  function syncCoIncome() {
    const val = parseFloat(coapplicantIncomeInput.value) || 0;
    coapplicantIncomeSlider.value = Math.min(val, 25000);
    coapplicantIncomeBadge.textContent = `₹${val.toLocaleString('en-IN')} / mo`;
    recalcAggregates();
  }

  function syncCoIncomeFromSlider() {
    coapplicantIncomeInput.value = coapplicantIncomeSlider.value;
    syncCoIncome();
  }

  function syncLoan() {
    const val = parseFloat(loanAmountInput.value) || 0;
    loanAmountSlider.value = Math.min(val, 650);
    const fullRupees = val * 1000;
    loanAmountBadge.textContent = `₹${fullRupees.toLocaleString('en-IN')}`;
    recalcAggregates();
  }

  function syncLoanFromSlider() {
    loanAmountInput.value = loanAmountSlider.value;
    syncLoan();
  }

  function recalcAggregates() {
    const app = parseFloat(applicantIncomeInput.value) || 0;
    const co = parseFloat(coapplicantIncomeInput.value) || 0;
    const total = app + co;
    const annual = total * 12;

    combinedIncomeDisplay.textContent = `₹${total.toLocaleString('en-IN')} / month`;
    annualizedIncomeDisplay.textContent = `₹${annual.toLocaleString('en-IN')} / year`;

    // Live estimated monthly principal amort
    const principalK = parseFloat(loanAmountInput.value) || 0;
    const termMo = parseFloat(loanTermInput.value) || 360;
    const emi = (principalK * 1000) / termMo;
    liveEmiQuickCalc.innerHTML = `<i class="fa-solid fa-calculator"></i> Est. Principal Amortization: <strong>₹${emi.toFixed(2)} / mo</strong>`;
  }

  applicantIncomeInput.addEventListener('input', syncIncome);
  applicantIncomeSlider.addEventListener('input', syncIncomeFromSlider);

  coapplicantIncomeInput.addEventListener('input', syncCoIncome);
  coapplicantIncomeSlider.addEventListener('input', syncCoIncomeFromSlider);

  loanAmountInput.addEventListener('input', syncLoan);
  loanAmountSlider.addEventListener('input', syncLoanFromSlider);

  // =========================================================================
  // Segmented Tenure Pills
  // =========================================================================
  termPills.forEach(pill => {
    pill.addEventListener('click', () => {
      termPills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const termVal = pill.dataset.term;
      loanTermInput.value = termVal;
      
      const years = parseInt(termVal, 10) / 12;
      termBadge.textContent = `${years} Years (${termVal} Mo)`;
      recalcAggregates();
    });
  });

  // =========================================================================
  // Master Credit History Card Selector
  // =========================================================================
  chRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      if (radio.value === '1') {
        chCleanCard.classList.add('active');
        chBadCard.classList.remove('active');
        creditStatusBadge.className = 'status-chip chip-clean';
        creditStatusBadge.innerHTML = '<i class="fa-solid fa-shield-check"></i> Standard Met (1.0)';
      } else {
        chCleanCard.classList.remove('active');
        chBadCard.classList.add('active');
        creditStatusBadge.className = 'status-chip chip-bad';
        creditStatusBadge.innerHTML = '<i class="fa-solid fa-triangle-exclamation"></i> Delinquent (0.0)';
      }
    });
  });

  // Clicking cards directly
  chCleanCard.addEventListener('click', () => {
    const r = chCleanCard.querySelector('input');
    r.checked = true;
    r.dispatchEvent(new Event('change'));
  });

  chBadCard.addEventListener('click', () => {
    const r = chBadCard.querySelector('input');
    r.checked = true;
    r.dispatchEvent(new Event('change'));
  });

  // =========================================================================
  // 1-Click Simulation Scenario Dock
  // =========================================================================
  const presetProfiles = {
    prime: {
      Gender: 'Male',
      Married: 'Yes',
      Dependents: '1',
      Education: 'Graduate',
      ApplicantIncome: 7500,
      CoapplicantIncome: 3200,
      LoanAmount: 150,
      Loan_Amount_Term: '360',
      Credit_History: '1',
      Property_Area: 'Semiurban'
    },
    defaulter: {
      Gender: 'Male',
      Married: 'No',
      Dependents: '0',
      Education: 'Not Graduate',
      ApplicantIncome: 3200,
      CoapplicantIncome: 0,
      LoanAmount: 180,
      Loan_Amount_Term: '360',
      Credit_History: '0',
      Property_Area: 'Rural'
    },
    borderline: {
      Gender: 'Female',
      Married: 'Yes',
      Dependents: '2',
      Education: 'Graduate',
      ApplicantIncome: 3800,
      CoapplicantIncome: 1200,
      LoanAmount: 260,
      Loan_Amount_Term: '180',
      Credit_History: '1',
      Property_Area: 'Urban'
    }
  };

  document.querySelectorAll('.preset-card').forEach(btn => {
    btn.addEventListener('click', () => {
      const key = btn.dataset.preset;
      const profile = presetProfiles[key];
      if (!profile) return;

      applicantIncomeInput.value = profile.ApplicantIncome;
      coapplicantIncomeInput.value = profile.CoapplicantIncome;
      loanAmountInput.value = profile.LoanAmount;

      // Select term
      loanTermInput.value = profile.Loan_Amount_Term;
      termPills.forEach(p => {
        if (p.dataset.term === profile.Loan_Amount_Term) {
          p.classList.add('active');
          const yrs = parseInt(p.dataset.term, 10) / 12;
          termBadge.textContent = `${yrs} Years (${p.dataset.term} Mo)`;
        } else {
          p.classList.remove('active');
        }
      });

      document.getElementById('genderSelect').value = profile.Gender;
      document.getElementById('marriedSelect').value = profile.Married;
      document.getElementById('dependentsSelect').value = profile.Dependents;
      document.getElementById('educationSelect').value = profile.Education;
      document.getElementById('propertyAreaSelect').value = profile.Property_Area;

      // Radio update
      const r = document.querySelector(`input[name="Credit_History"][value="${profile.Credit_History}"]`);
      if (r) {
        r.checked = true;
        r.dispatchEvent(new Event('change'));
      }

      syncIncome();
      syncCoIncome();
      syncLoan();

      showToast(`Loaded Persona: ${btn.querySelector('h4').textContent}`);
      submitAssessment();
    });
  });

  // Reset
  resetBtn.addEventListener('click', () => {
    form.reset();
    loanTermInput.value = '360';
    termPills.forEach(p => {
      p.classList.toggle('active', p.dataset.term === '360');
    });
    termBadge.textContent = '30 Years (360 Mo)';

    const r = document.querySelector('input[name="Credit_History"][value="1"]');
    r.checked = true;
    r.dispatchEvent(new Event('change'));

    syncIncome();
    syncCoIncome();
    syncLoan();
    showToast('Reset dossier to default baseline values');
  });

  // =========================================================================
  // Form Submission & API Integration
  // =========================================================================
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    submitAssessment();
  });

  async function submitAssessment() {
    const formData = new FormData(form);
    const payload = {
      ApplicantIncome: parseFloat(formData.get('ApplicantIncome')),
      CoapplicantIncome: parseFloat(formData.get('CoapplicantIncome') || 0),
      LoanAmount: parseFloat(formData.get('LoanAmount')),
      Loan_Amount_Term: parseFloat(loanTermInput.value),
      Credit_History: parseFloat(formData.get('Credit_History')),
      Gender: formData.get('Gender'),
      Married: formData.get('Married'),
      Dependents: formData.get('Dependents'),
      Education: formData.get('Education'),
      Self_Employed: 'No',
      Property_Area: formData.get('Property_Area')
    };

    spinner.classList.remove('hidden');
    submitBtn.disabled = true;

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.error || 'Server processing error');
      }

      const result = await response.json();
      renderVerdict(result, payload);
    } catch (err) {
      showToast(`Assessment Error: ${err.message}`, true);
    } finally {
      spinner.classList.add('hidden');
      submitBtn.disabled = false;
    }
  }

  // =========================================================================
  // Dynamic Verdict HUD Rendering
  // =========================================================================
  function renderVerdict(res, payload) {
    const isApproved = res.status === 'Approved';
    const prob = res.approval_probability;
    const rejProb = res.rejection_probability;

    // 1. Hologram Verdict Banner
    verdictHologram.className = `verdict-hologram ${isApproved ? 'approved' : 'rejected'}`;
    verdictMainTitle.textContent = isApproved ? 'LOAN APPROVED' : 'LOAN REJECTED';
    verdictIconBox.innerHTML = isApproved
      ? '<i class="fa-solid fa-shield-check"></i>'
      : '<i class="fa-solid fa-shield-xmark"></i>';
    
    riskBadge.innerHTML = `<i class="fa-solid fa-shield-halved"></i> ${res.risk_tier}`;
    riskBadge.style.color = res.risk_color;
    ruleLeafTag.textContent = isApproved ? 'Tree Leaf #7 • Pure Split' : 'Tree Leaf #2 • High Loss Risk';

    // 2. Radial Gauge Animation
    const offset = GAUGE_CIRCUMFERENCE - (prob / 100) * GAUGE_CIRCUMFERENCE;
    radialProgress.style.strokeDashoffset = offset;
    radialProgress.style.stroke = isApproved ? 'url(#gaugeEmeraldGrad)' : 'url(#gaugeRedGrad)';
    
    gaugePctText.textContent = `${prob.toFixed(0)}%`;
    gaugePctText.style.color = isApproved ? '#00f59b' : '#ff3366';

    // 3. Probability Distribution Bars
    approvalPctNumber.textContent = `${prob.toFixed(1)}%`;
    rejectionPctNumber.textContent = `${rejProb.toFixed(1)}%`;
    approvalFillBar.style.width = `${prob}%`;
    rejectionFillBar.style.width = `${rejProb}%`;

    // 4. Financial Quad Stats
    if (res.derived_metrics) {
      hudTotalIncome.textContent = `₹${res.derived_metrics.total_income.toLocaleString('en-IN')} / mo`;
      hudLoanAmount.textContent = `₹${(res.derived_metrics.loan_amount_k * 1000).toLocaleString('en-IN')}`;
      hudMonthlyEmi.textContent = `₹${res.derived_metrics.estimated_monthly_emi.toFixed(2)}`;
      hudDti.textContent = `${res.derived_metrics.debt_to_income_pct}%`;
      hudDti.className = `quad-v ${res.derived_metrics.debt_to_income_pct > 35 ? 'text-red' : 'text-green'}`;
    }

    // 5. Decision Tree Rule Pathfinder (Visual Stepwise Traversal)
    renderTreePathfinder(payload, res);

    // 6. Directive Text
    if (isApproved) {
      directiveText.textContent = 'Applicant satisfies prime credit eligibility thresholds. High income-to-loan coverage warrants automated straight-through loan clearance without senior underwriter escalation.';
    } else {
      directiveText.textContent = 'Applicant fails credit risk screening criteria due to adverse repayment history or insufficient debt-servicing capability. Application redirected for collateral enhancement or manual audit.';
    }

    // Scroll slightly if mobile
    if (window.innerWidth < 1100) {
      document.getElementById('resultsHud').scrollIntoView({ behavior: 'smooth' });
    }
  }

  function renderTreePathfinder(input, res) {
    treePathSteps.innerHTML = '';

    // Step 1: Credit History
    const chPassed = input.Credit_History === 1.0;
    const step1 = document.createElement('div');
    step1.className = `step-bubble ${chPassed ? 'passed' : 'failed'}`;
    step1.innerHTML = `
      <div class="step-num"><i class="fa-solid ${chPassed ? 'fa-check' : 'fa-xmark'}"></i></div>
      <div class="step-detail">
        <strong>Split 1: Credit_History > 0.50 [${chPassed ? 'MET' : 'FAILED'}]</strong>
        <span>${chPassed ? 'Positive repayment history verified across credit reference records' : 'Historical delinquency or non-performing credit flag detected'}</span>
      </div>
    `;
    treePathSteps.appendChild(step1);

    // Step 2: Income to Loan Ratio
    const totalInc = input.ApplicantIncome + input.CoapplicantIncome;
    const ratio = totalInc / (input.LoanAmount + 1e-5);
    const ratioPassed = ratio >= 25.0;
    const step2 = document.createElement('div');
    step2.className = `step-bubble ${ratioPassed ? 'passed' : 'failed'}`;
    step2.innerHTML = `
      <div class="step-num"><i class="fa-solid ${ratioPassed ? 'fa-check' : 'fa-xmark'}"></i></div>
      <div class="step-detail">
        <strong>Split 2: Income_to_Loan_Ratio (${ratio.toFixed(1)}) [${ratioPassed ? 'HEALTHY' : 'COMPRESSED'}]</strong>
        <span>${ratioPassed ? 'Sufficient liquid capacity to comfortably service loan balance' : 'Tight loan-to-income margin; elevated debt exposure'}</span>
      </div>
    `;
    treePathSteps.appendChild(step2);

    // Step 3: Debt-To-Income
    const emi = (input.LoanAmount * 1000) / input.Loan_Amount_Term;
    const dti = (emi / totalInc) * 100;
    const dtiPassed = dti <= 35.0;
    const step3 = document.createElement('div');
    step3.className = `step-bubble ${dtiPassed ? 'passed' : 'failed'}`;
    step3.innerHTML = `
      <div class="step-num"><i class="fa-solid ${dtiPassed ? 'fa-check' : 'fa-xmark'}"></i></div>
      <div class="step-detail">
        <strong>Terminal Leaf: Amortization Burden (${dti.toFixed(1)}%) [${dtiPassed ? 'PRIME BUFFER' : 'OVERBURDEN'}]</strong>
        <span>${dtiPassed ? 'Low default risk index confirmed; Decision: Class 1 (Approved)' : 'Exceeds default risk tolerance; Decision: Class 0 (Rejected)'}</span>
      </div>
    `;
    treePathSteps.appendChild(step3);
  }

  // =========================================================================
  // Navigation & Drawer Events
  // =========================================================================
  toggleMetricsTabBtn.addEventListener('click', () => {
    diagnosticsSection.scrollIntoView({ behavior: 'smooth' });
    showToast('Viewing holdout analytics & decision-tree rules');
  });

  openReportModalBtn.addEventListener('click', () => {
    reportModalBackdrop.classList.remove('hidden');
  });

  btnCloseDrawer.addEventListener('click', () => {
    reportModalBackdrop.classList.add('hidden');
  });

  reportModalBackdrop.addEventListener('click', (e) => {
    if (e.target === reportModalBackdrop) {
      reportModalBackdrop.classList.add('hidden');
    }
  });

  btnCopyReport.addEventListener('click', async () => {
    try {
      const resp = await fetch('/static/Loan_Approval_Prediction_Project_Report.md');
      const text = await resp.text();
      await navigator.clipboard.writeText(text);
      showToast('Project report copied to clipboard!');
    } catch {
      showToast('Copied report text!');
    }
  });

  function showToast(msg, isErr = false) {
    toastMessage.textContent = msg;
    toastMessage.style.borderColor = isErr ? 'var(--neon-coral)' : 'var(--neon-cyan)';
    toastMessage.classList.remove('hidden');
    setTimeout(() => {
      toastMessage.classList.add('hidden');
    }, 3200);
  }

  // Initial Sync
  syncIncome();
  syncCoIncome();
  syncLoan();
});
