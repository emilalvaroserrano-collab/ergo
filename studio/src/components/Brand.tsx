/**
 * The Ergo-V3 brand: the ERGO logo (icon + wordmark) from `assets/logo/ergo.png`, exported as a white-on-transparent
 * PNG in `public/logo`; `base.css` inverts it for the light theme and swaps to the icon-only mark on narrow screens.
 */
export function BrandLogo({ height = 15 }: { height?: number }) {
  return (
    <>
      <img class="brand-logo brand-wordmark" src="/logo/ergo-wordmark.png" height={height} alt="" aria-hidden="true" />
      <img class="brand-logo brand-mark" src="/logo/ergo-mark.png" height={height} alt="" aria-hidden="true" />
    </>
  );
}
