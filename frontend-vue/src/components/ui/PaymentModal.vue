<template>
  <!-- Modal Paiement -->
  <div class="modal-overlay" :class="{ active: modelValue }" @click.self="$emit('update:modelValue', false)">
    <div class="modal" style="max-width:560px">
      <div class="modal__header">
        <h2>Paiement de l'avance</h2>
        <button class="modal__close" @click="$emit('update:modelValue', false)">&times;</button>
      </div>

      <!-- Récap réservation -->
      <div style="background:var(--gray-50);border:1px solid var(--gray-200);border-radius:var(--radius-sm);padding:1rem;margin-bottom:1.5rem">
        <div style="font-size:.78rem;color:var(--gray-500);text-transform:uppercase;letter-spacing:.06em;margin-bottom:.75rem;font-weight:700">
          Récapitulatif
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
          <span class="text-muted">Chambre</span>
          <strong>N° {{ reservation?.room_detail?.number }}</strong>
        </div>
        <div style="display:flex;justify-content:space-between;font-size:.9rem;margin-bottom:.4rem">
          <span class="text-muted">{{ reservation?.nights }} nuit(s)</span>
          <strong>{{ formatPrice(reservation?.total_price) }}</strong>
        </div>
        <hr style="border:none;border-top:1px solid var(--gray-200);margin:.75rem 0">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <div style="font-size:.85rem;color:var(--gray-500)">Avance requise (5%)</div>
            <div style="font-size:.75rem;color:var(--gray-500)">Le reste sera réglé à l'arrivée</div>
          </div>
          <div style="font-size:1.75rem;font-weight:700;color:var(--gold-dark);font-family:var(--font-serif)">
            {{ formatPrice(advanceAmount) }}
          </div>
        </div>
      </div>

      <!-- Choix du moyen de paiement -->
      <div style="margin-bottom:1.5rem">
        <div class="form-label">Choisir votre moyen de paiement *</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:.75rem">

          <!-- Wave -->
          <button
            type="button"
            :class="['payment-method-btn', selectedMethod === 'wave' ? 'active' : '']"
            @click="selectedMethod = 'wave'"
          >
            <div class="payment-method-btn__logo" style="background:#1AB4FF">
              <span style="font-weight:900;font-size:.7rem;color:#fff;letter-spacing:-.5px">WAVE</span>
            </div>
            <div>
              <div style="font-weight:700;font-size:.9rem">Wave</div>
              <div style="font-size:.72rem;color:var(--gray-500)">Mobile Money</div>
            </div>
            <div class="payment-method-btn__check" v-if="selectedMethod === 'wave'">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </button>

          <!-- Orange Money -->
          <button
            type="button"
            :class="['payment-method-btn', selectedMethod === 'orange_money' ? 'active' : '']"
            @click="selectedMethod = 'orange_money'"
          >
            <div class="payment-method-btn__logo" style="background:#FF6600">
              <span style="font-weight:900;font-size:.55rem;color:#fff;letter-spacing:-.5px;text-align:center;line-height:1.1">OM</span>
            </div>
            <div>
              <div style="font-weight:700;font-size:.9rem">Orange Money</div>
              <div style="font-size:.72rem;color:var(--gray-500)">Mobile Money</div>
            </div>
            <div class="payment-method-btn__check" v-if="selectedMethod === 'orange_money'">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </button>

          <!-- Free Money -->
          <button
            type="button"
            :class="['payment-method-btn', selectedMethod === 'free_money' ? 'active' : '']"
            @click="selectedMethod = 'free_money'"
          >
            <div class="payment-method-btn__logo" style="background:#E4002B">
              <span style="font-weight:900;font-size:.6rem;color:#fff;letter-spacing:-.5px;text-align:center;line-height:1.1">FREE<br>MONEY</span>
            </div>
            <div>
              <div style="font-weight:700;font-size:.9rem">Free Money</div>
              <div style="font-size:.72rem;color:var(--gray-500)">Mobile Money</div>
            </div>
            <div class="payment-method-btn__check" v-if="selectedMethod === 'free_money'">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </button>

          <!-- Carte bancaire -->
          <button
            type="button"
            :class="['payment-method-btn', selectedMethod === 'card' ? 'active' : '']"
            @click="selectedMethod = 'card'"
          >
            <div class="payment-method-btn__logo" style="background:var(--navy)">
              <span style="font-weight:900;font-size:.55rem;color:#fff;letter-spacing:-.5px;text-align:center;line-height:1.1">CARTE<br>BANCAIRE</span>
            </div>
            <div>
              <div style="font-weight:700;font-size:.9rem">Carte bancaire</div>
              <div style="font-size:.72rem;color:var(--gray-500)">Visa / Mastercard</div>
            </div>
            <div class="payment-method-btn__check" v-if="selectedMethod === 'card'">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
            </div>
          </button>
        </div>
      </div>

      <!-- Numéro de téléphone (pour mobile money) -->
      <div v-if="['wave','orange_money','free_money'].includes(selectedMethod)" class="form-group">
        <label class="form-label">Numéro de téléphone *</label>
        <div style="display:flex;gap:.5rem;align-items:center">
          <span style="padding:.75rem .875rem;background:var(--gray-50);border:1.5px solid var(--gray-300);border-radius:var(--radius-sm);font-weight:600;color:var(--navy);white-space:nowrap">🇸🇳 +221</span>
          <input
            v-model="phoneNumber"
            type="tel"
            class="form-control"
            placeholder="77 000 00 00"
            maxlength="12"
          />
        </div>
      </div>

      <!-- Infos carte (si carte bancaire) -->
      <div v-if="selectedMethod === 'card'" class="form-group">
        <label class="form-label">Numéro de carte *</label>
        <input type="text" class="form-control" placeholder="0000 0000 0000 0000" v-model="cardNumber" maxlength="19" />
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-top:.75rem">
          <div>
            <label class="form-label">Expiration *</label>
            <input type="text" class="form-control" placeholder="MM/AA" v-model="cardExpiry" maxlength="5" />
          </div>
          <div>
            <label class="form-label">CVV *</label>
            <input type="password" class="form-control" placeholder="•••" v-model="cardCvv" maxlength="3" />
          </div>
        </div>
      </div>

      <!-- Note informative -->
      <div style="background:rgba(212,160,23,.08);border:1px solid rgba(212,160,23,.25);border-radius:var(--radius-sm);padding:.875rem;margin-bottom:1.5rem;font-size:.85rem;color:var(--navy)">
        <strong>ℹ Information :</strong> Le montant de <strong>{{ formatPrice(advanceAmount) }}</strong> 
        correspond à une avance de 5% pour confirmer votre réservation. 
        Le solde de <strong>{{ formatPrice(balanceAmount) }}</strong> sera réglé à votre arrivée.
      </div>

      <button
        type="button"
        class="btn btn--primary btn--full btn--lg"
        :disabled="!selectedMethod || processing"
        @click="processPayment"
      >
        <span v-if="processing">Traitement en cours…</span>
        <span v-else>Payer {{ formatPrice(advanceAmount) }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { paymentsAPI } from '@/services/api';
import { useNotificationStore } from '@/stores/notification';
import { formatPrice } from '@/utils/formatters';

const props = defineProps({
  modelValue:  { type: Boolean, default: false },
  reservation: { type: Object,  default: null },
});

const emit = defineEmits(['update:modelValue', 'paid']);

const notif = useNotificationStore();

const selectedMethod = ref('wave');
const phoneNumber    = ref('');
const cardNumber     = ref('');
const cardExpiry     = ref('');
const cardCvv        = ref('');
const processing     = ref(false);

// 5% du total
// Sécurité : si total_price est 0 ou absent, on affiche 0 avec un avertissement
const advanceAmount = computed(() => {
  const total = parseFloat(props.reservation?.total_price || 0);
  if (total <= 0) return 0;
  return Math.ceil(total * 0.05);
});

const balanceAmount = computed(() => {
  const total = parseFloat(props.reservation?.total_price || 0);
  return Math.max(0, total - advanceAmount.value);
});

async function processPayment() {
  if (!selectedMethod.value) return;

  // Validation basique
  if (['wave','orange_money','free_money'].includes(selectedMethod.value) && !phoneNumber.value) {
    notif.showToast('Veuillez entrer votre numéro de téléphone.', 'error');
    return;
  }
  if (selectedMethod.value === 'card' && (!cardNumber.value || !cardExpiry.value || !cardCvv.value)) {
    notif.showToast('Veuillez remplir tous les champs de la carte.', 'error');
    return;
  }

  processing.value = true;
  try {
    await paymentsAPI.create({
      reservation: props.reservation.id,
      amount: advanceAmount.value,
      method: selectedMethod.value,
    });
    notif.showToast('Paiement effectué ! Votre réservation est confirmée.', 'success');
    emit('update:modelValue', false);
    emit('paid');
  } catch (err) {
    notif.showToast(err.message, 'error');
  } finally {
    processing.value = false;
  }
}
</script>

<style scoped>
.payment-method-btn {
  display: flex;
  align-items: center;
  gap: .75rem;
  padding: .875rem;
  background: var(--white);
  border: 1.5px solid var(--gray-200);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
  text-align: left;
  position: relative;
  font-family: var(--font-sans);
}
.payment-method-btn:hover {
  border-color: var(--navy);
  background: var(--gray-50);
}
.payment-method-btn.active {
  border-color: var(--navy);
  background: rgba(11,31,58,.04);
  box-shadow: 0 0 0 3px rgba(11,31,58,.10);
}
.payment-method-btn__logo {
  width: 42px; height: 42px;
  border-radius: var(--radius-xs);
  display: grid; place-items: center;
  flex-shrink: 0;
}
.payment-method-btn__check {
  position: absolute;
  top: .5rem; right: .5rem;
  width: 20px; height: 20px;
  background: var(--navy);
  border-radius: 50%;
  display: grid; place-items: center;
}
</style>
