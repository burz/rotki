<template>
  <tr class="font-weight-medium append-row" :class="formattedClassName">
    <td v-if="leftPatchColspan >= 1 && !isMobile" :colspan="leftPatchColspan" />
    <td :colspan="labelColspan" :class="{ 'd-flex align-center': isMobile }">
      {{ label }}
    </td>
    <slot name="custom-columns" />
    <td
      v-if="$slots.default"
      class="text-end"
      :class="{ 'd-flex align-center': isMobile }"
    >
      <slot />
    </td>
    <td
      v-if="rightPatchColspan >= 1 && !isMobile"
      :colspan="rightPatchColspan"
    />
  </tr>
</template>
<script lang="ts">
import { computed, defineComponent, toRefs } from '@vue/composition-api';

export default defineComponent({
  name: 'RowAppend',
  props: {
    className: { required: false, type: [String, Object], default: '' },
    label: { required: false, type: String, default: '' },
    labelColspan: { required: false, type: [Number, String], default: 1 },
    leftPatchColspan: { required: false, type: [Number, String], default: 0 },
    isMobile: { required: true, type: Boolean },
    rightPatchColspan: { required: false, type: [Number, String], default: 0 }
  },
  setup(props) {
    const { className, isMobile } = toRefs(props);

    const formattedClassName = computed(() => {
      const propClassName =
        typeof className.value === 'object'
          ? className.value
          : {
              [className.value]: true
            };

      return {
        'd-flex justify-space-between': isMobile.value,
        ...propClassName
      };
    });

    return {
      formattedClassName
    };
  }
});
</script>
<style scoped lang="scss">
.append {
  &-row {
    &:hover {
      background-color: transparent !important;
    }
  }
}
</style>
