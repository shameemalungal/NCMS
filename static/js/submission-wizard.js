document.addEventListener("DOMContentLoaded", function () {

    // =====================================================
    // ELEMENTS
    // =====================================================

    const form = document.getElementById("wizardForm");

    if (!form) {
        return;
    }

    const pages = [
        document.getElementById("step1"),
        document.getElementById("step2"),
        document.getElementById("step3")
    ];

    const wizardSteps =
        document.querySelectorAll(".wizard-step");

    const nextBtn =
        document.getElementById("nextBtn");

    const prevBtn =
        document.getElementById("prevBtn");

    const submitBtn =
        document.getElementById("submitBtn");

    const reviewContainer =
        document.getElementById("reviewContainer");

    const targetElement =
        document.getElementById("targetValue");

    const daysWorked =
        document.getElementById("days_worked");

    const vaccinations =
        document.getElementById("vaccinations");

    const entries =
        document.getElementById("entries");

    const diseased =
        document.getElementById("diseased");

    const below4Months =
        document.getElementById("below_4_months");

    const pregnant =
        document.getElementById("pregnant");

    const unwilling =
        document.getElementById("unwilling");

    const otherCount =
        document.getElementById("other_count");

    const otherReason =
        document.getElementById("other_reason");

    const remarks =
        document.getElementById("remarks");

    const vaccinationReason =
        document.getElementById("vaccination_reason");

    const pashudhanReason =
        document.getElementById("pashudhan_reason");

    const vaccinationReasonSection =
        document.getElementById(
            "vaccinationReasonSection"
        );

    const pashudhanReasonSection =
        document.getElementById(
            "pashudhanReasonSection"
        );

    const vaccinationPercent =
        document.getElementById("vaccinationPercent");

    const entryPercent =
        document.getElementById("entryPercent");

    const vaccinationBar =
        document.getElementById("vaccinationBar");

    const entryBar =
        document.getElementById("entryBar");

    const remainingAnimals =
        document.getElementById("remainingAnimals");


    // =====================================================
    // STATE
    // =====================================================

    let currentStep = 1;

    const totalSteps = 3;

    const target =
        targetElement
            ? parseInt(targetElement.textContent) || 0
            : 0;


    // =====================================================
    // HELPER FUNCTIONS
    // =====================================================

    function numberValue(element) {

        if (!element) {
            return 0;
        }

        return parseInt(element.value) || 0;
    }


    function textValue(element) {

        if (!element) {
            return "";
        }

        return element.value.trim();
    }


    function formatNumber(value) {

        return Number(value || 0).toLocaleString("en-IN");
    }


    // =====================================================
    // CALCULATIONS
    // =====================================================

    function calculate() {

        const vaccinated =
            numberValue(vaccinations);

        const pashudhan =
            numberValue(entries);

        let vaccinationPercentage = 0;
        let pashudhanPercentage = 0;

        if (target > 0) {

            vaccinationPercentage =
                (vaccinated / target) * 100;
        }

        if (vaccinated > 0) {

            pashudhanPercentage =
                (pashudhan / vaccinated) * 100;
        }


        // Vaccination %

        if (vaccinationPercent) {

            vaccinationPercent.textContent =
                vaccinationPercentage.toFixed(2) + "%";
        }

        // =====================================================
        // LOW ACHIEVEMENT REASONS
        // =====================================================

        // Vaccination achievement:
        // vaccinations / target × 100

        if (vaccinationReasonSection) {

            if (
                vaccinated > 0 &&
                vaccinationPercentage >= 83
            ) {

                vaccinationReasonSection.classList.add("d-none");

                if (vaccinationReason) {
                    vaccinationReason.value = "";
                }

            } else {

                vaccinationReasonSection.classList.remove("d-none");
            }
        }


        // Pashudhan achievement:
        // entries / vaccinations × 100

        if (pashudhanReasonSection) {

            if (
                vaccinated > 0 &&
                pashudhanPercentage >= 97
            ) {

                pashudhanReasonSection.classList.add("d-none");

                if (pashudhanReason) {
                    pashudhanReason.value = "";
                }

            } else {

                pashudhanReasonSection.classList.remove("d-none");
            }
        }

        if (vaccinationBar) {

            vaccinationBar.style.width =
                Math.min(
                    vaccinationPercentage,
                    100
                ) + "%";
        }


        // Pashudhan %

        if (entryPercent) {

            entryPercent.textContent =
                pashudhanPercentage.toFixed(2) + "%";
        }


        if (entryBar) {

            entryBar.style.width =
                Math.min(
                    pashudhanPercentage,
                    100
                ) + "%";
        }


        // Remaining animals

        if (remainingAnimals) {

            remainingAnimals.textContent =
                formatNumber(
                    Math.max(
                        target - vaccinated,
                        0
                    )
                );
        }

        // -----------------------------------------------------
        // Conditional reason fields
        // -----------------------------------------------------

        if (vaccinationReasonSection) {

            if (
                vaccinated > 0 &&
                vaccinationPercentage < 83
            ) {

                vaccinationReasonSection
                    .classList.remove("d-none");

            } else {

                vaccinationReasonSection
                    .classList.add("d-none");
            }
        }


        if (pashudhanReasonSection) {

            if (
                vaccinated > 0 &&
                pashudhanPercentage < 97
            ) {

                pashudhanReasonSection
                    .classList.remove("d-none");

            } else {

                pashudhanReasonSection
                    .classList.add("d-none");
            }
        }

    }


    // =====================================================
    // VALIDATION
    // =====================================================

    function validateStep1() {

        const worked =
            numberValue(daysWorked);

        const vaccinated =
            numberValue(vaccinations);

        const pashudhan =
            numberValue(entries);


        // Clear previous validation

        [
            daysWorked,
            vaccinations,
            entries
        ].forEach(function (field) {

            if (field) {
                field.classList.remove("is-invalid");
            }

        });


        // Days worked

        if (worked < 0) {

            daysWorked.classList.add("is-invalid");

            alert(
                "Squad Days Worked cannot be negative."
            );

            daysWorked.focus();

            return false;
        }


        // Vaccination

        if (vaccinated < 0) {

            vaccinations.classList.add("is-invalid");

            alert(
                "Number of vaccinations cannot be negative."
            );

            vaccinations.focus();

            return false;
        }


        // Pashudhan

        if (pashudhan < 0) {

            entries.classList.add("is-invalid");

            alert(
                "Pashudhan entries cannot be negative."
            );

            entries.focus();

            return false;
        }


        // Entries should not normally exceed vaccinations

        if (pashudhan > vaccinated) {

            entries.classList.add("is-invalid");

            alert(
                "Pashudhan entries cannot be greater than vaccinations done."
            );

            entries.focus();

            return false;
        }

        // Vaccination reason required below 83%

        let vaccinationPercentage = 0;

        if (target > 0) {

            vaccinationPercentage =
                (vaccinated / target) * 100;
        }


        if (
            vaccinated > 0 &&
            vaccinationPercentage < 83 &&
            vaccinationReason &&
            textValue(vaccinationReason) === ""
        ) {

            alert(
                "Please enter the reason for vaccination achievement below 83%."
            );

            vaccinationReason.focus();

            return false;
        }


        // Pashudhan reason required below 97%

        let pashudhanPercentage = 0;

        if (vaccinated > 0) {

            pashudhanPercentage =
                (pashudhan / vaccinated) * 100;
        }


        if (
            vaccinated > 0 &&
            pashudhanPercentage < 97 &&
            pashudhanReason &&
            textValue(pashudhanReason) === ""
        ) {

            alert(
                "Please enter the reason for Pashudhan achievement below 97%."
            );

            pashudhanReason.focus();

            return false;
        }


        return true;
    }


    // =====================================================
    // REVIEW
    // =====================================================

    function buildReview() {

        if (!reviewContainer) {
            return;
        }

        const vaccinated =
            numberValue(vaccinations);

        const pashudhan =
            numberValue(entries);

        let vaccinationPercentage = 0;
        let pashudhanPercentage = 0;

        if (target > 0) {

            vaccinationPercentage =
                (vaccinated / target) * 100;
        }

        if (vaccinated > 0) {

            pashudhanPercentage =
                (pashudhan / vaccinated) * 100;
        }


        reviewContainer.innerHTML = `

            <div class="row g-3">

                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">

                            <small class="text-muted">
                                Days Worked
                            </small>

                            <h4 class="mt-2 mb-0">
                                ${formatNumber(
                                    numberValue(daysWorked)
                                )}
                            </h4>

                        </div>
                    </div>
                </div>


                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">

                            <small class="text-muted">
                                Vaccinations Done
                            </small>

                            <h4 class="mt-2 mb-0">
                                ${formatNumber(vaccinated)}
                            </h4>

                            <small class="text-success">
                                ${vaccinationPercentage.toFixed(2)}%
                                of target
                            </small>

                        </div>
                    </div>
                </div>


                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">

                            <small class="text-muted">
                                Pashudhan Entries
                            </small>

                            <h4 class="mt-2 mb-0">
                                ${formatNumber(pashudhan)}
                            </h4>

                            <small class="text-info">
                                ${pashudhanPercentage.toFixed(2)}%
                                of target
                            </small>

                        </div>
                    </div>
                </div>

            </div>


            <div class="card mt-4">

                <div class="card-header">
                    <strong>Leftover Details</strong>
                </div>

                <div class="card-body">

                    <div class="row g-3">

                        <div class="col-md-4">
                            <small class="text-muted">
                                Diseased
                            </small>
                            <div class="fw-semibold">
                                ${formatNumber(
                                    numberValue(diseased)
                                )}
                            </div>
                        </div>

                        <div class="col-md-4">
                            <small class="text-muted">
                                Below 4 Months
                            </small>
                            <div class="fw-semibold">
                                ${formatNumber(
                                    numberValue(below4Months)
                                )}
                            </div>
                        </div>

                        <div class="col-md-4">
                            <small class="text-muted">
                                Pregnant
                            </small>
                            <div class="fw-semibold">
                                ${formatNumber(
                                    numberValue(pregnant)
                                )}
                            </div>
                        </div>

                        <div class="col-md-4">
                            <small class="text-muted">
                                Unwilling
                            </small>
                            <div class="fw-semibold">
                                ${formatNumber(
                                    numberValue(unwilling)
                                )}
                            </div>
                        </div>

                        <div class="col-md-4">
                            <small class="text-muted">
                                Other
                            </small>
                            <div class="fw-semibold">
                                ${formatNumber(
                                    numberValue(otherCount)
                                )}
                            </div>
                        </div>

                        <div class="col-md-4">
                            <small class="text-muted">
                                Other Reason
                            </small>
                            <div class="fw-semibold">
                                ${escapeHtml(
                                    textValue(otherReason) || "-"
                                )}
                            </div>
                        </div>

                    </div>

                </div>

            </div>


            ${
                vaccinationReason
                ? `
                <div class="mt-4">
                    <small class="text-muted">
                        Vaccination Achievement Reason
                    </small>
                    <div class="fw-semibold mt-1">
                        ${escapeHtml(
                            textValue(vaccinationReason) || "-"
                        )}
                    </div>
                </div>
                `
                : ""
            }


            ${
                pashudhanReason
                ? `
                <div class="mt-3">
                    <small class="text-muted">
                        Pashudhan Achievement Reason
                    </small>
                    <div class="fw-semibold mt-1">
                        ${escapeHtml(
                            textValue(pashudhanReason) || "-"
                        )}
                    </div>
                </div>
                `
                : ""
            }


            <div class="mt-3">

                <small class="text-muted">
                    Remarks
                </small>

                <div class="fw-semibold mt-1">
                    ${escapeHtml(
                        textValue(remarks) || "-"
                    )}
                </div>

            </div>
        `;
    }


    // =====================================================
    // SAFE HTML
    // =====================================================

    function escapeHtml(value) {

        const div =
            document.createElement("div");

        div.textContent = value;

        return div.innerHTML;
    }


    // =====================================================
    // SHOW STEP
    // =====================================================

    function showStep(step) {

        currentStep = step;


        // Pages

        pages.forEach(function (page, index) {

            if (!page) {
                return;
            }

            const pageNumber = index + 1;

            if (pageNumber === currentStep) {

                page.classList.remove("d-none");
                page.classList.add("active");

            } else {

                page.classList.add("d-none");
                page.classList.remove("active");
            }

        });


        // Progress indicator

        wizardSteps.forEach(function (wizardStep) {

            const stepNumber =
                parseInt(
                    wizardStep.dataset.step
                );

            wizardStep.classList.remove(
                "active",
                "completed"
            );

            if (stepNumber < currentStep) {

                wizardStep.classList.add(
                    "completed"
                );

            } else if (
                stepNumber === currentStep
            ) {

                wizardStep.classList.add(
                    "active"
                );
            }

        });


        // Previous button

        if (currentStep === 1) {

            prevBtn.style.display = "none";

        } else {

            prevBtn.style.display = "inline-block";
        }


        // Next / Submit buttons

        if (currentStep === totalSteps) {

            nextBtn.classList.add("d-none");

            submitBtn.classList.remove("d-none");

        } else {

            nextBtn.classList.remove("d-none");

            submitBtn.classList.add("d-none");
        }


        // Build review when entering step 2

        if (currentStep === 2) {

            buildReview();
        }


        // Scroll to form area

        form.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    }


    // =====================================================
    // NEXT BUTTON
    // =====================================================

    nextBtn.addEventListener(
        "click",
        function () {

            if (currentStep === 1) {

                if (!validateStep1()) {
                    return;
                }

                calculate();
                buildReview();
            }


            if (currentStep < totalSteps) {

                showStep(
                    currentStep + 1
                );
            }
        }
    );


    // =====================================================
    // PREVIOUS BUTTON
    // =====================================================

    prevBtn.addEventListener(
        "click",
        function () {

            if (currentStep > 1) {

                showStep(
                    currentStep - 1
                );
            }
        }
    );


    // =====================================================
    // LIVE CALCULATION
    // =====================================================

    [
        vaccinations,
        entries
    ].forEach(function (field) {

        if (!field) {
            return;
        }

        field.addEventListener(
            "input",
            calculate
        );

        field.addEventListener(
            "change",
            calculate
        );
    });


    // =====================================================
    // INITIALIZE
    // =====================================================

    calculate();

    showStep(1);

});