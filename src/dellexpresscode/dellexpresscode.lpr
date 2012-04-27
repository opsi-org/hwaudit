program dellexpresscode;

{$MODE Delphi}
{$H+}

{$APPTYPE CONSOLE}

//code derivated from:
//http://theroadtodelphi.wordpress.com/2011/04/21/accesing-the-wmi-from-delphi-and-fpc-via-com-without-late-binding-or-wbemscripting_tlb/


uses
  Windows,
  Variants,
  SysUtils,
  strutils,
  ActiveX,
  JwaWbemCli;

const
  RPC_C_AUTHN_LEVEL_DEFAULT = 0;
  RPC_C_IMP_LEVEL_IMPERSONATE = 3;
  RPC_C_AUTHN_WINNT = 10;
  RPC_C_AUTHZ_NONE = 0;
  RPC_C_AUTHN_LEVEL_CALL = 3;
  EOAC_NONE = 0;


  function myNumb2Dec(S: string; B: Byte): Uint64;
  var
    I: Longint;
    P: Uint64;
  begin
    I := Length(S);
    Result := 0;
    S := UpperCase(S);
    P := 1;
    while (I >= 1) do begin
      if S[I] > '@' then Result := Result + (Ord(S[I]) - 55) * P
      else Result := Result + (Ord(S[I]) - 48) * P;
      Dec(I);
      P := P * B;
    end;
  end;

procedure IWbemServices_ExecQuery;
const
  strLocale    = '';
  strUser      = '';
  strPassword  = '';
  strNetworkResource = 'root\cimv2';
  strAuthority       = '';
  WQL1                = 'Select Manufacturer from Win32_ComputerSystem';
  WQL2                = 'Select SerialNumber from Win32_SystemEnclosure';

var
  FWbemLocator         : IWbemLocator;
  FWbemServices        : IWbemServices;
  FUnsecuredApartment  : IUnsecuredApartment;
  ppEnum               : IEnumWbemClassObject;
  apObjects            : IWbemClassObject;
  puReturned           : ULONG;
  pDesc, pIP, pMac, pVal     : OleVariant;
  pType                : Integer;
  plFlavor             : Integer;
  Succeed              : HRESULT;
  I : Integer;
  vendor, serial, expresscode : string;
  myi : integer;
  bigi : UInt64;

begin
  // Set general COM security levels --------------------------
  // Note: If you are using Windows 2000, you need to specify -
  // the default authentication credentials for a user by using
  // a SOLE_AUTHENTICATION_LIST structure in the pAuthList ----
  // parameter of CoInitializeSecurity ------------------------
  if Failed(CoInitializeSecurity(nil, -1, nil, nil, RPC_C_AUTHN_LEVEL_DEFAULT, RPC_C_IMP_LEVEL_IMPERSONATE, nil, EOAC_NONE, nil)) then Exit;
  // Obtain the initial locator to WMI -------------------------
  if Succeeded(CoCreateInstance(CLSID_WbemLocator, nil, CLSCTX_INPROC_SERVER, IID_IWbemLocator, FWbemLocator)) then
  try
    // Connect to WMI through the IWbemLocator::ConnectServer method
    if Succeeded(FWbemLocator.ConnectServer(strNetworkResource, strUser, strPassword, strLocale,  WBEM_FLAG_CONNECT_USE_MAX_WAIT, strAuthority, nil, FWbemServices)) then
    try
      // Set security levels on the proxy -------------------------
      if Failed(CoSetProxyBlanket(FWbemServices, RPC_C_AUTHN_WINNT, RPC_C_AUTHZ_NONE, nil, RPC_C_AUTHN_LEVEL_CALL, RPC_C_IMP_LEVEL_IMPERSONATE, nil, EOAC_NONE)) then Exit;
      if Succeeded(CoCreateInstance(CLSID_UnsecuredApartment, nil, CLSCTX_LOCAL_SERVER, IID_IUnsecuredApartment, FUnsecuredApartment)) then
      try
        // Use the IWbemServices pointer to make requests of WMI
        //Succeed := FWbemServices.ExecQuery('WQL', WQL, WBEM_FLAG_FORWARD_ONLY OR WBEM_FLAG_RETURN_IMMEDIATELY, nil, ppEnum);
        Succeed := FWbemServices.ExecQuery('WQL', WQL1, WBEM_FLAG_FORWARD_ONLY, nil, ppEnum);
        if Succeeded(Succeed) then
        begin
           // Get the data from the query
           while (ppEnum.Next(WBEM_INFINITE, 1, apObjects, puReturned)=0) do
           begin
             apObjects.Get('Manufacturer', 0, pVal, pType, plFlavor);
             //writeln('Manufacturer: '+  VarToStr(pVal));
             vendor :=  VarToStr(pVal);
             VarClear(pVal);
           end;
        end
        else
        Writeln(Format('Error executing WQL sentence %x',[Succeed]));



        if pos('dell',LowerCase(vendor)) > 0 then
        begin
          // Use the IWbemServices pointer to make requests of WMI
          //Succeed := FWbemServices.ExecQuery('WQL', WQL, WBEM_FLAG_FORWARD_ONLY OR WBEM_FLAG_RETURN_IMMEDIATELY, nil, ppEnum);
          Succeed := FWbemServices.ExecQuery('WQL', WQL2, WBEM_FLAG_FORWARD_ONLY, nil, ppEnum);
          if Succeeded(Succeed) then
          begin
             // Get the data from the query
             while (ppEnum.Next(WBEM_INFINITE, 1, apObjects, puReturned)=0) do
             begin
               apObjects.Get('serialnumber', 0, pVal, pType, plFlavor);
               //writeln('SerialNumber: '+  VarToStr(pVal));
               writeln('dellexpresscode='+ inttostr(myNumb2Dec(VarToStr(pVal),36)));
               //writeln('dell expresscode: '+ inttostr(myNumb2Dec('2y4955j',36)));
               VarClear(pVal);
             end;
          end
          else
          Writeln(Format('Error executing WQL sentence %x',[Succeed]));
        end;
      finally
        FUnsecuredApartment := nil;
      end;
    finally
      FWbemServices := nil;
    end;
  finally
    FWbemLocator := nil;
  end;
end;

{$R *.res}

begin
  try
      // Initialize COM. ------------------------------------------
    if Succeeded(CoInitializeEx(nil, COINIT_MULTITHREADED)) then
    try
      IWbemServices_ExecQuery;
    finally
      CoUninitialize();
    end;
  except
      on E:Exception do
      writeln('Error in ip2mac: '+E.Message);
  end;
  exit;
end.
