const menuToggle = document.getElementById("menuToggle");
      const navLinks = document.getElementById("navLinks");
      const bookingForm = document.getElementById("bookingForm");
      const serviceSelect = document.getElementById("serviceSelect");
      const selectedPrice = document.getElementById("selectedPrice");
      const bookingNote = document.getElementById("bookingNote");
      const dateInput = document.getElementById("appointmentDate");
      const checkoutSection = document.getElementById("checkout");
      const checkoutNote = document.getElementById("checkoutNote");
      const checkoutName = document.getElementById("checkoutName");
      const checkoutService = document.getElementById("checkoutService");
      const checkoutDate = document.getElementById("checkoutDate");
      const checkoutAmount = document.getElementById("checkoutAmount");
      const checkoutClose = document.getElementById("checkoutClose");
      const payFlutterwave = document.getElementById("payFlutterwave");
      const payStripe = document.getElementById("payStripe");
      const bookingCreateUrl = bookingForm?.getAttribute("action") || "";
      const bookedSlotsUrl = bookingForm?.dataset.bookedSlotsUrl || "";
      const paymentMethodUrlTemplate =
        bookingForm?.dataset.paymentMethodUrlTemplate || "";
      let activeBookingId = null;
      const serviceDetails = {
        "Signature Self-Care Session": "$55 / 75min",
        "Hair Artistry": "$45+ / 60min+",
        "General Consultation": "$0 / 15min",
        "Classic Fade": "$25 / 30min",
        "Temp Fade + Design": "$35 / 45min",
        "Full Cut & Beard": "$45 / 60min",
        "Kids Cut": "$15 / 25min",
        "Women's Trim": "$35 / 45min",
        "Silk Press": "$65 / 90min",
        "Color Refresh": "$75 / 120min",
        "Luxury Blowout": "$45 / 60min",
        "Classic Manicure": "$25 / 35min",
        "Gel Manicure": "$32 / 45min",
        "Signature Pedicure": "$38 / 45min",
        "Deluxe Mani + Pedi": "$70 / 90min",
        Microblading: "30k / Consult",
        "Ombre Brow": "40k / Consult",
        "Combo Brow": "50k / Consult",
        "Nano Brow": "60k / Consult",
        "Classic Lash Extension": "12k / Consult",
        "Hybrid Lash Extension": "18k / Consult",
        "Volume Lash Extension": "25k / Consult",
        "Classic Cluster Lash": "10k / Consult",
        "Hybrid Cluster Lash": "15k / Consult",
        "Volume Cluster Lash": "18k / Consult",
        "Brow Training": "Confirm in studio / Training",
        "Lash Training": "Confirm in studio / Training",
        "Beauty Training": "Confirm in studio / Training",
      };

      const today = new Date();
      today.setHours(0, 0, 0, 0);
      dateInput.min = today.toISOString().split("T")[0];

      const bookingSection = document.getElementById("booking");
      const generatedServiceOptions = new Set();
      const appointmentTimeSelect = document.getElementById("appointmentTime");
      let bookedAppointments = [];

      const getBookedAppointments = () => bookedAppointments;

      const fetchBookedAppointments = () => {
        if (!bookedSlotsUrl) return Promise.resolve([]);
        const params = new URLSearchParams();
        if (dateInput.value) params.set("date", dateInput.value);
        return fetch(`${bookedSlotsUrl}?${params.toString()}`)
          .then((response) => response.json())
          .then((data) => {
            bookedAppointments = data.booked_slots || [];
            return bookedAppointments;
          })
          .catch(() => []);
      };

      const updateAvailableTimeSlots = () => {
        const selectedDate = dateInput.value;
        if (!selectedDate) {
          Array.from(appointmentTimeSelect.options).forEach((option) => {
            if (option.value) option.disabled = false;
          });
          return;
        }

        fetchBookedAppointments().then((booked) => {
          const bookedTimes = booked
            .filter((slot) => slot.date === selectedDate)
            .map((slot) => slot.time);

          Array.from(appointmentTimeSelect.options).forEach((option) => {
            if (option.value) {
              option.disabled = bookedTimes.includes(option.value);
            }
          });
        });
      };

      dateInput.addEventListener("change", updateAvailableTimeSlots);

      const normalizeService = (text) =>
        String(text || "")
          .trim()
          .toLowerCase();

      const findServiceOption = (service) => {
        const normalizedService = normalizeService(service);
        return Array.from(serviceSelect.options).find((option) => {
          return (
            normalizeService(option.value) === normalizedService ||
            normalizeService(option.textContent) === normalizedService
          );
        });
      };

      const getServicePriceDetails = (option) => {
        if (!option) return "Confirmed after consultation";
        const price = option.dataset.price || "";
        const duration = option.dataset.duration || "";
        if (price || duration) {
          return [price, duration].filter(Boolean).join(" / ");
        }
        return (
          serviceDetails[option.value] ||
          serviceDetails[option.textContent] ||
          "Confirmed after consultation"
        );
      };

      const setBookingService = (service, price = "", duration = "") => {
        if (!service) return;

        const trimmedService = String(service).trim();
        const match = findServiceOption(trimmedService);
        if (match) {
          match.selected = true;
          if (price) match.dataset.price = price;
          if (duration) match.dataset.duration = duration;
        } else {
          const newOption = document.createElement("option");
          newOption.value = trimmedService;
          newOption.textContent = trimmedService;
          newOption.dataset.generated = "true";
          if (price) newOption.dataset.price = price;
          if (duration) newOption.dataset.duration = duration;
          serviceSelect.appendChild(newOption);
          generatedServiceOptions.add(trimmedService);
          newOption.selected = true;
        }

        serviceSelect.dispatchEvent(new Event("change", { bubbles: true }));
        const selectedOption = serviceSelect.selectedOptions[0];
        selectedPrice.value =
          [
            price || selectedOption?.dataset.price,
            duration || selectedOption?.dataset.duration,
          ]
            .filter(Boolean)
            .join(" / ") || getServicePriceDetails(selectedOption);
      };

      const getBookingScrollTop = () => {
        const headerHeight =
          document.querySelector(".site-header")?.offsetHeight || 0;
        const elementTop =
          bookingSection.getBoundingClientRect().top + window.pageYOffset;
        return Math.max(elementTop - headerHeight - 16, 0);
      };

      const scrollToBooking = () => {
        if (!bookingSection) return;
        window.scrollTo({ top: getBookingScrollTop(), behavior: "smooth" });
        window.history.replaceState(null, "", "#booking");
        setTimeout(() => document.getElementById("firstName").focus(), 500);
      };

      const updateCheckout = (booking) => {
        checkoutName.textContent = booking.fullName || "Client";
        checkoutService.textContent = booking.service || "Selected service";
        checkoutDate.textContent =
          [booking.date, booking.time].filter(Boolean).join(" at ") ||
          "Appointment date";
        checkoutAmount.textContent =
          booking.session || "Confirmed after consultation";
      };

      const openCheckout = () => {
        if (!checkoutSection) return;
        checkoutSection.classList.add("is-open");
        document.body.classList.add("checkout-open");
        window.history.replaceState(null, "", "#checkout");
      };

      const closeCheckout = () => {
        checkoutSection.classList.remove("is-open");
        document.body.classList.remove("checkout-open");
        window.history.replaceState(null, "", "#booking");
      };
      const getSelectedPaymentMethod = () =>
        document.querySelector('input[name="paymentMethod"]:checked')?.value || "";

      const showPendingPaymentNote = (provider) => {
        if (!getSelectedPaymentMethod()) {
          checkoutNote.innerHTML = `<strong>Choose a payment method.</strong><br>Select a payment option first so the studio knows how to verify your payment.`;
          checkoutNote.classList.add("show");
          return;
        }

        checkoutNote.innerHTML = `<strong>Booking received.</strong><br>Your booking is pending until the manager confirms your ${provider} payment in Django admin.`;
        checkoutNote.classList.add("show");
      };

      const getCsrfToken = () =>
        bookingForm.querySelector('input[name="csrfmiddlewaretoken"]')?.value ||
        "";

      const updatePaymentMethod = () => {
        const paymentMethod = getSelectedPaymentMethod();
        if (!activeBookingId || !paymentMethod || !paymentMethodUrlTemplate) {
          return;
        }

        const url = paymentMethodUrlTemplate.replace("/0/", `/${activeBookingId}/`);
        const formData = new FormData();
        formData.set("payment_method", paymentMethod);

        fetch(url, {
          method: "POST",
          body: formData,
          headers: {
            "X-CSRFToken": getCsrfToken(),
            "X-Requested-With": "XMLHttpRequest",
          },
        })
          .then((response) => {
            if (!response.ok) throw new Error("Payment method update failed");
            return response.json();
          })
          .then((data) => {
            checkoutNote.innerHTML = `<strong>Payment method saved.</strong><br>${data.paymentMethodDisplay} is recorded for manager verification.`;
            checkoutNote.classList.add("show");
          })
          .catch(() => {
            checkoutNote.innerHTML = `<strong>Payment method not saved.</strong><br>Please try selecting the payment option again.`;
            checkoutNote.classList.add("show");
          });
      };

      document.querySelectorAll(".price-list").forEach((list) => {
        const items = Array.from(list.querySelectorAll(".price-item"));
        if (items.length <= 2) return;

        items.slice(2).forEach((item) => item.classList.add("price-extra"));
        const toggle = document.createElement("button");
        toggle.className = "price-toggle";
        toggle.type = "button";
        toggle.textContent = `View ${items.length - 2} more options`;
        list.insertAdjacentElement("afterend", toggle);
        toggle.addEventListener("click", () => {
          const isOpen = list.classList.toggle("is-open");
          toggle.textContent = isOpen
            ? "Show fewer options"
            : `View ${items.length - 2} more options`;
        });
      });

      menuToggle.addEventListener("click", () => {
        const isOpen = navLinks.classList.toggle("show");
        menuToggle.setAttribute("aria-expanded", String(isOpen));
      });

      document.querySelectorAll(".nav-links a").forEach((link) => {
        link.addEventListener("click", () => {
          navLinks.classList.remove("show");
          menuToggle.setAttribute("aria-expanded", "false");
        });
      });

      document.querySelectorAll(".js-book").forEach((button) => {
        button.addEventListener("click", (event) => {
          event.preventDefault();
          const service = (button.dataset.service || "").trim();
          const price = (button.dataset.price || "").trim();
          const duration = (button.dataset.duration || "").trim();

          setBookingService(service, price, duration);
          bookingNote.classList.remove("show");
          scrollToBooking();
        });
      });

      serviceSelect.addEventListener("change", () => {
        if (!serviceSelect.value) {
          selectedPrice.value = "";
          return;
        }

        selectedPrice.value = getServicePriceDetails(
          serviceSelect.selectedOptions[0],
        );
      });

      payFlutterwave.addEventListener("click", () =>
        showPendingPaymentNote("Flutterwave/card"),
      );

      payStripe.addEventListener("click", () => showPendingPaymentNote("Stripe"));

      document
        .querySelectorAll('input[name="paymentMethod"]')
        .forEach((input) => input.addEventListener("change", updatePaymentMethod));

      checkoutClose.addEventListener("click", closeCheckout);

      checkoutSection.addEventListener("click", (event) => {
        if (event.target === checkoutSection) closeCheckout();
      });
      bookingForm.addEventListener("submit", (event) => {
        event.preventDefault();
        bookingNote.classList.remove("show");

        const serviceOption = serviceSelect.selectedOptions[0];
        const serviceName =
          serviceOption?.textContent?.trim() || serviceSelect.value || "";
        const sessionDetails = getServicePriceDetails(serviceOption);
        selectedPrice.value = sessionDetails;

        const formData = new FormData(bookingForm);
        const booking = {
          fullName:
            `${formData.get("firstName")} ${formData.get("lastName")}`.trim(),
          firstName: formData.get("firstName"),
          lastName: formData.get("lastName"),
          email: formData.get("clientEmail"),
          phone: formData.get("clientPhone"),
          service: serviceName,
          date: formData.get("appointmentDate"),
          time: formData.get("appointmentTime"),
          session:
            formData.get("selectedPrice") ||
            sessionDetails ||
            "Confirmed after consultation",
          paymentMethod: getSelectedPaymentMethod(),
          notes: formData.get("notes"),
        };

        if (!booking.service) {
          bookingNote.innerHTML = `<strong>Please select a service.</strong><br>Choose a service before booking.`;
          bookingNote.classList.add("show");
          return;
        }

        formData.set("service", booking.service);
        formData.set("session", booking.session);
        formData.set("payment_method", booking.paymentMethod);

        fetch(bookingCreateUrl, {
          method: "POST",
          body: formData,
          headers: { "X-Requested-With": "XMLHttpRequest" },
        })
          .then((response) =>
            response.json().then((data) => ({ ok: response.ok, data })),
          )
          .then(({ ok, data }) => {
            if (!ok) {
              const errors = data.errors
                ? Object.values(data.errors).flat().join("<br>")
                : "Please check the booking details and try again.";
              bookingNote.innerHTML = `<strong>Booking could not be saved.</strong><br>${errors}`;
              bookingNote.classList.add("show");
              return;
            }

            updateCheckout(data.booking || booking);
            activeBookingId = data.booking?.id || null;
            bookingNote.innerHTML = `<strong>Booking submitted.</strong><br>Your appointment is pending until the manager confirms payment in Django admin.`;
            bookingNote.classList.add("show");
            updateAvailableTimeSlots();
            openCheckout();
          })
          .catch(() => {
            bookingNote.innerHTML = `<strong>Booking could not be saved.</strong><br>Please try again or contact the studio directly.`;
            bookingNote.classList.add("show");
          });
      });

      updateAvailableTimeSlots();
