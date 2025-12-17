import type { ComputedRef } from 'vue';
import type { FormItemSetupProps } from './FormItem';
import type { FormItemRule, Size } from './interface';
export declare function formItemSize(props: FormItemSetupProps): {
    mergedSize: ComputedRef<Size>;
};
export declare function formItemMisc(props: FormItemSetupProps): {
    validationErrored: import("vue").Ref<boolean, boolean>;
    validationWarned: import("vue").Ref<boolean, boolean>;
    mergedLabelStyle: ComputedRef<import("vue").StyleValue[]>;
    mergedLabelPlacement: ComputedRef<import("./interface").LabelPlacement>;
    mergedLabelAlign: ComputedRef<import("./interface").LabelAlign | undefined>;
    mergedShowRequireMark: ComputedRef<boolean | undefined>;
    mergedRequireMarkPlacement: ComputedRef<"left" | "right" | "right-hanging">;
    mergedValidationStatus: ComputedRef<"warning" | "error" | "success" | undefined>;
    mergedShowFeedback: ComputedRef<boolean>;
    mergedShowLabel: ComputedRef<boolean>;
    isAutoLabelWidth: ComputedRef<boolean>;
};
export declare function formItemRule(props: FormItemSetupProps): {
    mergedRules: ComputedRef<FormItemRule[]>;
    mergedRequired: ComputedRef<boolean>;
};
